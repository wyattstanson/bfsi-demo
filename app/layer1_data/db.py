"""Layer 1 — Data Foundation: connections to the two stores that matter.

Two stores, by deliberate design (see README data-store note):
  * The **ledger** (system of record): Postgres when DATABASE_URL is set, else a
    local SQLite file.  Append-only truth; NOT on the hot path.
    # PROD: swap Postgres for Snowflake + Databricks (lakehouse).
  * The **online store** (hot path): Redis when REDIS_URL is set, else an
    in-process dict.  Sub-millisecond reads for /decide.
    # PROD: swap Redis for ElastiCache / DynamoDB.

No general-purpose or document store is added — it would be neither the ledger
nor on the hot path.
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from typing import Any, Iterable

from app import config

# --------------------------------------------------------------------------- #
# Ledger (system of record)
# --------------------------------------------------------------------------- #
_PG = bool(config.DATABASE_URL)
if _PG:
    import psycopg  # type: ignore
    from psycopg.types.json import Json as _PgJson  # type: ignore


def as_json(obj: Any):
    """Adapt a dict/list for a JSON column: a JSONB adapter on Postgres, a
    plain JSON string on SQLite (TEXT).  Callers use this instead of json.dumps
    so the same INSERT works against both backends."""
    return _PgJson(obj) if _PG else json.dumps(obj)


def from_json(value: Any):
    """Inverse of as_json for reads: Postgres JSONB already decodes to a Python
    object; SQLite hands back a string that needs parsing."""
    if value is None or isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return value

_local = threading.local()


def _connect():
    if _PG:
        return psycopg.connect(config.DATABASE_URL, autocommit=True)
    conn = sqlite3.connect(config.SQLITE_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def conn():
    """One connection per thread (both drivers are not thread-safe to share)."""
    c = getattr(_local, "conn", None)
    if c is None:
        c = _local.conn = _connect()
    return c


def _translate(sql: str) -> str:
    """Tests and modules write portable SQL with '?' placeholders."""
    if _PG:
        return sql.replace("?", "%s")
    return sql


def execute(sql: str, params: Iterable[Any] = ()) -> None:
    cur = conn().cursor()
    cur.execute(_translate(sql), tuple(params))
    if not _PG:
        conn().commit()


def executemany(sql: str, rows: Iterable[Iterable[Any]]) -> None:
    cur = conn().cursor()
    cur.executemany(_translate(sql), [tuple(r) for r in rows])
    if not _PG:
        conn().commit()


def fetchall(sql: str, params: Iterable[Any] = ()) -> list[tuple]:
    cur = conn().cursor()
    cur.execute(_translate(sql), tuple(params))
    return cur.fetchall()


def fetchone(sql: str, params: Iterable[Any] = ()) -> tuple | None:
    cur = conn().cursor()
    cur.execute(_translate(sql), tuple(params))
    return cur.fetchone()


# Portable column types (Postgres vs SQLite differ on autoincrement / json).
_PK = "SERIAL PRIMARY KEY" if _PG else "INTEGER PRIMARY KEY AUTOINCREMENT"
_JSON = "JSONB" if _PG else "TEXT"


def init_schema() -> None:
    """Create the ledger tables.  Idempotent."""
    execute(
        f"""
        CREATE TABLE IF NOT EXISTS party (
            party_id      TEXT PRIMARY KEY,
            domain        TEXT,
            journey_stage TEXT,
            name          TEXT,          -- PII: never leaves the server / never scored
            email         TEXT,          -- PII
            ssn           TEXT,          -- PII
            age           INTEGER,
            income        REAL,
            balance       REAL,
            tenure_months INTEGER,
            risk_band     TEXT,
            fairness_group TEXT,         -- protected attribute, audit-only
            consent_ref   TEXT,
            consent_marketing INTEGER
        )
        """
    )
    execute(
        f"""
        CREATE TABLE IF NOT EXISTS txn (
            id        {_PK},
            party_id  TEXT,
            ts        REAL,
            amount    REAL,
            mcc       TEXT,
            channel   TEXT,
            is_flagged INTEGER
        )
        """
    )
    # Offline feature table (Layer 2 batch output).
    execute(
        f"""
        CREATE TABLE IF NOT EXISTS feature_offline (
            party_id TEXT,
            fname    TEXT,
            fvalue   REAL,
            computed_ts REAL,
            PRIMARY KEY (party_id, fname)
        )
        """
    )
    # Vector memory for the agent (pgvector in prod; JSON text here).
    # PROD: swap fvector TEXT for pgvector `vector(64)` and an ivfflat index.
    execute(
        f"""
        CREATE TABLE IF NOT EXISTS agent_memory (
            id       {_PK},
            party_id TEXT,
            kind     TEXT,
            text     TEXT,
            embedding {_JSON},
            ts       REAL
        )
        """
    )
    # Layer 5 append-only audit log — the 16 regulated fields.
    execute(
        f"""
        CREATE TABLE IF NOT EXISTS audit_log (
            decision_id       TEXT PRIMARY KEY,
            party_id          TEXT,
            channel           TEXT,
            use_case          TEXT,
            action_id         TEXT,
            features_snapshot {_JSON},
            model_versions    {_JSON},
            score             REAL,
            reason_codes      {_JSON},
            fairness_flag     TEXT,
            mode              TEXT,
            latency_ms        REAL,
            consent_ref       TEXT,
            ts                REAL,
            human_reviewed    INTEGER,
            override          TEXT
        )
        """
    )
    execute(
        f"""
        CREATE TABLE IF NOT EXISTS human_queue (
            id        {_PK},
            party_id  TEXT,
            goal      TEXT,
            reason    TEXT,
            context   {_JSON},
            ts        REAL,
            resolved  INTEGER
        )
        """
    )


# --------------------------------------------------------------------------- #
# Online store (hot path)
# --------------------------------------------------------------------------- #
class InMemoryStore:
    """Stand-in for Redis: a thread-safe dict of hashes.

    # PROD: swap for ElastiCache (Redis) / DynamoDB.  Same get/put contract.
    """

    def __init__(self) -> None:
        self._h: dict[str, dict[str, str]] = {}
        self._lock = threading.Lock()
        self.backend = "in-memory"

    def hset(self, key: str, mapping: dict[str, Any]) -> None:
        with self._lock:
            self._h.setdefault(key, {}).update({k: str(v) for k, v in mapping.items()})

    def hgetall(self, key: str) -> dict[str, str]:
        with self._lock:
            return dict(self._h.get(key, {}))

    def rpush(self, key: str, value: str) -> None:
        with self._lock:
            self._h.setdefault("__lists__:" + key, {})[str(time.time_ns())] = value


class RedisStore:
    """Thin wrapper so the two backends share one contract."""

    def __init__(self, url: str) -> None:
        import redis  # type: ignore

        self._r = redis.from_url(url, decode_responses=True)
        self.backend = "redis"

    def hset(self, key: str, mapping: dict[str, Any]) -> None:
        self._r.hset(key, mapping={k: str(v) for k, v in mapping.items()})

    def hgetall(self, key: str) -> dict[str, str]:
        return self._r.hgetall(key)

    def rpush(self, key: str, value: str) -> None:
        self._r.rpush(key, value)


_store: RedisStore | InMemoryStore | None = None


def get_online_store():
    """Singleton hot-path store."""
    global _store
    if _store is None:
        if config.REDIS_URL:
            try:
                _store = RedisStore(config.REDIS_URL)
            except Exception:
                _store = InMemoryStore()
        else:
            _store = InMemoryStore()
    return _store


def backends() -> dict[str, str]:
    return {
        "ledger": "postgres" if _PG else "sqlite",
        "online_store": get_online_store().backend,
    }
