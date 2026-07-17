from __future__ import annotations
import json
import sqlite3
import threading
import time
from typing import Any, Iterable
from app import config
_PG = bool(config.DATABASE_URL)
if _PG:
    import psycopg
    from psycopg.types.json import Json as _PgJson

def as_json(obj: Any):
    return _PgJson(obj) if _PG else json.dumps(obj)

def from_json(value: Any):
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
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    return conn

def conn():
    c = getattr(_local, 'conn', None)
    if c is None:
        c = _local.conn = _connect()
    return c

def _translate(sql: str) -> str:
    if _PG:
        return sql.replace('?', '%s')
    return sql

def execute(sql: str, params: Iterable[Any]=()) -> None:
    cur = conn().cursor()
    cur.execute(_translate(sql), tuple(params))
    if not _PG:
        conn().commit()

def executemany(sql: str, rows: Iterable[Iterable[Any]]) -> None:
    cur = conn().cursor()
    cur.executemany(_translate(sql), [tuple(r) for r in rows])
    if not _PG:
        conn().commit()

def fetchall(sql: str, params: Iterable[Any]=()) -> list[tuple]:
    cur = conn().cursor()
    cur.execute(_translate(sql), tuple(params))
    return cur.fetchall()

def fetchone(sql: str, params: Iterable[Any]=()) -> tuple | None:
    cur = conn().cursor()
    cur.execute(_translate(sql), tuple(params))
    return cur.fetchone()
_PK = 'SERIAL PRIMARY KEY' if _PG else 'INTEGER PRIMARY KEY AUTOINCREMENT'
_JSON = 'JSONB' if _PG else 'TEXT'

def init_schema() -> None:
    execute(f'\n        CREATE TABLE IF NOT EXISTS party (\n            party_id      TEXT PRIMARY KEY,\n            domain        TEXT,\n            journey_stage TEXT,\n            region        TEXT,\n            currency      TEXT,\n            name          TEXT,\n            email         TEXT,\n            ssn           TEXT,\n            age           INTEGER,\n            income        REAL,\n            balance       REAL,\n            tenure_months INTEGER,\n            risk_band     TEXT,\n            fairness_group TEXT,\n            consent_ref   TEXT,\n            consent_marketing INTEGER\n        )\n        ')
    execute(f'\n        CREATE TABLE IF NOT EXISTS txn (\n            id        {_PK},\n            party_id  TEXT,\n            ts        REAL,\n            amount    REAL,\n            mcc       TEXT,\n            channel   TEXT,\n            is_flagged INTEGER\n        )\n        ')
    execute(f'\n        CREATE TABLE IF NOT EXISTS feature_offline (\n            party_id TEXT,\n            fname    TEXT,\n            fvalue   REAL,\n            computed_ts REAL,\n            PRIMARY KEY (party_id, fname)\n        )\n        ')
    execute(f'\n        CREATE TABLE IF NOT EXISTS agent_memory (\n            id       {_PK},\n            party_id TEXT,\n            kind     TEXT,\n            text     TEXT,\n            embedding {_JSON},\n            ts       REAL\n        )\n        ')
    execute(f'\n        CREATE TABLE IF NOT EXISTS audit_log (\n            decision_id       TEXT PRIMARY KEY,\n            party_id          TEXT,\n            channel           TEXT,\n            use_case          TEXT,\n            action_id         TEXT,\n            features_snapshot {_JSON},\n            model_versions    {_JSON},\n            score             REAL,\n            reason_codes      {_JSON},\n            fairness_flag     TEXT,\n            mode              TEXT,\n            latency_ms        REAL,\n            consent_ref       TEXT,\n            ts                REAL,\n            human_reviewed    INTEGER,\n            override          TEXT\n        )\n        ')
    execute(f'\n        CREATE TABLE IF NOT EXISTS human_queue (\n            id        {_PK},\n            party_id  TEXT,\n            goal      TEXT,\n            reason    TEXT,\n            context   {_JSON},\n            ts        REAL,\n            resolved  INTEGER\n        )\n        ')

class InMemoryStore:

    def __init__(self) -> None:
        self._h: dict[str, dict[str, str]] = {}
        self._lock = threading.Lock()
        self.backend = 'in-memory'

    def hset(self, key: str, mapping: dict[str, Any]) -> None:
        with self._lock:
            self._h.setdefault(key, {}).update({k: str(v) for k, v in mapping.items()})

    def hgetall(self, key: str) -> dict[str, str]:
        with self._lock:
            return dict(self._h.get(key, {}))

    def rpush(self, key: str, value: str) -> None:
        with self._lock:
            self._h.setdefault('__lists__:' + key, {})[str(time.time_ns())] = value

class RedisStore:

    def __init__(self, url: str) -> None:
        import redis
        self._r = redis.from_url(url, decode_responses=True)
        self.backend = 'redis'

    def hset(self, key: str, mapping: dict[str, Any]) -> None:
        self._r.hset(key, mapping={k: str(v) for k, v in mapping.items()})

    def hgetall(self, key: str) -> dict[str, str]:
        return self._r.hgetall(key)

    def rpush(self, key: str, value: str) -> None:
        self._r.rpush(key, value)
_store: RedisStore | InMemoryStore | None = None

def get_online_store():
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
    return {'ledger': 'postgres' if _PG else 'sqlite', 'online_store': get_online_store().backend}
