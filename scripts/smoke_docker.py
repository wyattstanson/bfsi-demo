"""Smoke test against the real stack: Postgres (pgvector) + Redis via docker.

Brings the compose services up, points the app at them, exercises every layer
end to end, and asserts the writes actually landed in Postgres / that Redis is
the live hot-path store — then (optionally) tears the services down.

    python -m scripts.smoke_docker            # up, test, leave running
    python -m scripts.smoke_docker --down     # up, test, then compose down

This is the same application code as the offline demo; only the backends differ.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Point the app at the compose services BEFORE importing any app module
# (app.config reads these at import time).
os.environ.setdefault("DATABASE_URL", "postgresql://bfsi:bfsi@localhost:5432/bfsi")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("SEED_PARTIES", "400")


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=str(ROOT), **kw)


def _require(cond: bool, msg: str) -> None:
    if not cond:
        print(f"  FAIL: {msg}")
        raise SystemExit(1)
    print(f"  ok: {msg}")


def compose_up() -> None:
    # Probe the daemon with a hard timeout: a half-started Docker Desktop leaves
    # `docker ps` blocking on its named pipe, so never wait on it unbounded.
    try:
        probe = _run(["docker", "ps"], capture_output=True, timeout=15)
        daemon_ok = probe.returncode == 0
    except subprocess.TimeoutExpired:
        daemon_ok = False
    if not daemon_ok:
        print("Docker daemon is not reachable — start Docker Desktop (needs a WSL2 "
              "or Hyper-V backend) and retry.")
        raise SystemExit(2)
    # --wait blocks until healthchecks (defined in docker-compose.yml) pass.
    r = _run(["docker", "compose", "up", "-d", "--wait"], timeout=300)
    if r.returncode != 0:
        print("compose up failed")
        raise SystemExit(2)


def compose_down() -> None:
    _run(["docker", "compose", "down", "-v"])


def smoke() -> None:
    # Imported here so the env vars above are already set.
    from fastapi.testclient import TestClient

    from app import config
    from app.layer1_data import db
    from app.main import app

    _require(bool(config.DATABASE_URL), "DATABASE_URL is set (Postgres)")
    _require(bool(config.REDIS_URL), "REDIS_URL is set (Redis)")

    with TestClient(app) as client:  # triggers bootstrap against Postgres
        backends = client.get("/health").json()["backends"]
        print("  backends:", backends)
        _require(backends["ledger"] == "postgres", "ledger backend is Postgres")
        _require(backends["online_store"] == "redis", "hot-path store is Redis")

        party = client.get("/personas?limit=1").json()[0]["party_id"]

        # --- Layer 4/5: a governed decision, warm latency, one audit row ------
        for _ in range(15):  # warm up
            client.post("/decide", json={"party_id": party, "event": {"event_type": "session_start"}})
        before = client.get("/governance").json()["audit_rows"]
        r = client.post("/decide", json={
            "party_id": party, "channel": "web",
            "event": {"event_type": "large_transfer_attempt", "amount": 4000}}).json()
        after = client.get("/governance").json()["audit_rows"]
        _require(after == before + 1, "exactly one new audit row written")
        _require(r["latency_ms"] < config.LATENCY_SLO_MS,
                 f"warm latency {r['latency_ms']}ms < {config.LATENCY_SLO_MS}ms SLO")

        # Verify the row + its JSONB columns are readable straight from Postgres.
        row = client.get(f"/audit/{r['decision_id']}").json()
        _require(isinstance(row["reason_codes"], list) and bool(row["features_snapshot"]),
                 "JSONB audit columns round-trip through Postgres")
        pg_count = db.fetchone("SELECT COUNT(*) FROM audit_log WHERE decision_id = ?",
                               (r["decision_id"],))[0]
        _require(pg_count == 1, "audit row is queryable in Postgres by decision_id")

        # --- Agentic layer: escalation lands in the human_queue table ---------
        hq_before = db.fetchone("SELECT COUNT(*) FROM human_queue")[0]
        client.post("/agent", json={"party_id": party,
                                    "goal": "dispute an unauthorized charge of 15000"})
        hq_after = db.fetchone("SELECT COUNT(*) FROM human_queue")[0]
        _require(hq_after == hq_before + 1, "agent escalation enqueued in Postgres human_queue")

        # --- Vector memory round-trips through Postgres -----------------------
        mem = db.fetchone("SELECT COUNT(*) FROM agent_memory")[0]
        _require(mem > 0, f"agent_memory populated in Postgres ({mem} rows)")

    print("\nSMOKE TEST PASSED — full stack (Postgres + Redis) healthy.")


def main() -> int:
    tear_down = "--down" in sys.argv
    compose_up()
    try:
        # Give Postgres a beat past healthcheck for connection readiness.
        time.sleep(2)
        smoke()
    finally:
        if tear_down:
            compose_down()
        else:
            print("\n(services left running; `docker compose down -v` to stop)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
