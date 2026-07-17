from __future__ import annotations
import time
import uuid
from app.layer1_data import db
FIELDS = ['decision_id', 'party_id', 'channel', 'use_case', 'action_id', 'features_snapshot', 'model_versions', 'score', 'reason_codes', 'fairness_flag', 'mode', 'latency_ms', 'consent_ref', 'ts', 'human_reviewed', 'override']
assert len(FIELDS) == 16

def new_decision_id() -> str:
    return f'dec_{uuid.uuid4().hex[:16]}'

def write(row: dict) -> None:
    values = (row['decision_id'], row['party_id'], row['channel'], row['use_case'], row['action_id'], db.as_json(row['features_snapshot']), db.as_json(row['model_versions']), float(row['score']), db.as_json(row['reason_codes']), row['fairness_flag'], row['mode'], float(row['latency_ms']), row['consent_ref'], row.get('ts', time.time()), int(row.get('human_reviewed', 0)), row.get('override', ''))
    db.execute('INSERT INTO audit_log (' + ','.join(FIELDS) + ') VALUES (' + ','.join(['?'] * 16) + ')', values)

def count() -> int:
    return db.fetchone('SELECT COUNT(*) FROM audit_log')[0]

def get(decision_id: str) -> dict | None:
    row = db.fetchone('SELECT ' + ','.join(FIELDS) + ' FROM audit_log WHERE decision_id = ?', (decision_id,))
    if not row:
        return None
    d = dict(zip(FIELDS, row))
    for k in ('features_snapshot', 'model_versions', 'reason_codes'):
        d[k] = db.from_json(d[k])
    return d
