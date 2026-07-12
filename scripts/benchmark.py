"""Fire N /decide requests and print p50/p95/p99; assert p99 under the SLO.

Runs in-process against the app (no server needed) by default.  Set BASE_URL to
benchmark a running server over real HTTP instead.
"""
from __future__ import annotations

import os
import sys
import time

from app import config


def _percentile(xs, p):
    xs = sorted(xs)
    k = max(0, min(len(xs) - 1, int(round((p / 100.0) * (len(xs) - 1)))))
    return xs[k]


def run(n: int = 500) -> int:
    base = os.getenv("BASE_URL")
    body = {"party_id": None, "channel": "web",
            "event": {"event_type": "large_transfer_attempt", "amount": 4000}}

    if base:
        import httpx

        cli = httpx.Client(base_url=base, timeout=10)
        get = lambda path: cli.get(path).json()
        post = lambda path, j: cli.post(path, json=j).json()
    else:
        from fastapi.testclient import TestClient
        from app.main import app

        tc = TestClient(app).__enter__()
        get = lambda path: tc.get(path).json()
        post = lambda path, j: tc.post(path, json=j).json()

    body["party_id"] = get("/personas?limit=1")[0]["party_id"]

    for _ in range(25):          # warm-up
        post("/decide", body)

    server_lat, wall_lat = [], []
    for _ in range(n):
        t0 = time.perf_counter()
        r = post("/decide", body)
        wall_lat.append((time.perf_counter() - t0) * 1000)
        server_lat.append(r["latency_ms"])

    print(f"transport: {'HTTP ' + base if base else 'in-process TestClient'}")
    print(f"samples: {n}")
    for label, lat in (("server decision", server_lat), ("client wall", wall_lat)):
        print(f"  {label:16s}  p50={_percentile(lat,50):6.2f}ms  "
              f"p95={_percentile(lat,95):6.2f}ms  p99={_percentile(lat,99):6.2f}ms")

    p99 = _percentile(server_lat, 99)
    ok = p99 < config.LATENCY_SLO_MS
    print(f"\nSLO {config.LATENCY_SLO_MS}ms  ->  p99 {p99:.2f}ms  [{'PASS' if ok else 'FAIL'}]")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(run(int(sys.argv[1]) if len(sys.argv) > 1 else 500))
