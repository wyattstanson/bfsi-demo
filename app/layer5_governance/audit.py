from __future__ import annotations
import threading
import time
import uuid
from app.layer1_data import db
FIELDS = ['decision_id', 'party_id', 'channel', 'use_case', 'action_id', 'features_snapshot', 'model_versions', 'score', 'reason_codes', 'fairness_flag', 'mode', 'latency_ms', 'consent_ref', 'ts', 'human_reviewed', 'override']
assert len(FIELDS) == 16
_lock = threading.Lock()
_pending: list[tuple] = []
_pending_ids: dict[str, dict] = {}
_committed: int | None = None
_INSERT = 'INSERT INTO audit_log (' + ','.join(FIELDS) + ') VALUES (' + ','.join(['?'] * 16) + ')'


def new_decision_id() -> str:
    return f'dec_{uuid.uuid4().hex[:16]}'


def _init_committed() -> None:
    global _committed
    if _committed is None:
        _committed = db.fetchone('SELECT COUNT(*) FROM audit_log')[0]


def write(row: dict) -> None:
    ts = row.get('ts', time.time())
    values = (row['decision_id'], row['party_id'], row['channel'], row['use_case'], row['action_id'], db.as_json(row['features_snapshot']), db.as_json(row['model_versions']), float(row['score']), db.as_json(row['reason_codes']), row['fairness_flag'], row['mode'], float(row['latency_ms']), row['consent_ref'], ts, int(row.get('human_reviewed', 0)), row.get('override', ''))
    rec = {f: row.get(f) for f in FIELDS}
    rec['ts'] = ts
    with _lock:
        _pending.append(values)
        _pending_ids[row['decision_id']] = rec


def flush() -> int:
    with _lock:
        if not _pending:
            return 0
        batch = _pending[:]
        db.executemany(_INSERT, batch)
        n = len(batch)
        _init_committed()
        global _committed
        _committed += n
        _pending.clear()
        _pending_ids.clear()
    return n


def count() -> int:
    with _lock:
        _init_committed()
        return _committed + len(_pending)


def get(decision_id: str) -> dict | None:
    with _lock:
        if decision_id in _pending_ids:
            return _pending_ids[decision_id]
    row = db.fetchone('SELECT ' + ','.join(FIELDS) + ' FROM audit_log WHERE decision_id = ?', (decision_id,))
    if not row:
        return None
    d = dict(zip(FIELDS, row))
    for k in ('features_snapshot', 'model_versions', 'reason_codes'):
        d[k] = db.from_json(d[k])
    return d
