from __future__ import annotations
import re
import time
from app.layer1_data import db
_SEG = re.compile('^[a-z0-9]+(_[a-z0-9]+)*$')

def _validate(name: str) -> str:
    parts = name.split('__')
    if len(parts) != 4 or not all((_SEG.match(p) for p in parts)):
        raise ValueError(f"feature '{name}' violates domain__entity__metric__window convention")
    return name
FEATURES = ['retail__party__txn_count__90d', 'retail__party__txn_amount_sum__90d', 'retail__party__txn_amount_avg__90d', 'payments__party__flagged_ratio__90d', 'wealth__party__balance__now', 'nbfc__party__tenure__months', 'retail__party__income__now', 'retail__party__age__now']
for _f in FEATURES:
    _validate(_f)

def _online_key(party_id: str) -> str:
    return f'features:{party_id}'

def _attrs_key(party_id: str) -> str:
    return f'attrs:{party_id}'
ATTR_COLS = ['domain', 'journey_stage', 'region', 'currency', 'age', 'balance', 'risk_band', 'consent_ref', 'consent_marketing', 'fairness_group']

def _feats(row: dict, n: int, total: float, flagged: int) -> dict[str, float]:
    return {'retail__party__txn_count__90d': float(n), 'retail__party__txn_amount_sum__90d': round(total, 2), 'retail__party__txn_amount_avg__90d': round(total / n, 2) if n else 0.0, 'payments__party__flagged_ratio__90d': round(flagged / n, 4) if n else 0.0, 'wealth__party__balance__now': float(row['balance']), 'nbfc__party__tenure__months': float(row['tenure_months']), 'retail__party__income__now': float(row['income']), 'retail__party__age__now': float(row['age'])}

def compute_offline(party_id: str, row: dict) -> dict[str, float]:
    txns = db.fetchall('SELECT amount, is_flagged FROM txn WHERE party_id = ?', (party_id,))
    n = len(txns)
    total = sum((a for a, _ in txns))
    flagged = sum((f for _, f in txns))
    return _feats(row, n, total, flagged)

def materialize(limit: int | None=None) -> int:
    agg = {pid: (n, tot or 0.0, fl or 0) for pid, n, tot, fl in db.fetchall('SELECT party_id, COUNT(*), SUM(amount), SUM(is_flagged) FROM txn GROUP BY party_id')}
    cols = 'party_id, balance, tenure_months, income, age, domain, journey_stage, region, currency, risk_band, consent_ref, consent_marketing, fairness_group'
    sql = f'SELECT {cols} FROM party'
    if limit:
        sql += f' LIMIT {int(limit)}'
    parties = db.fetchall(sql)
    store = db.get_online_store()
    now = time.time()
    offline_rows = []
    for party_id, balance, tenure, income, age, domain, stage, region, currency, risk_band, consent_ref, consent_mkt, fairness_group in parties:
        n, total, flagged = agg.get(party_id, (0, 0.0, 0))
        feats = _feats({'balance': balance, 'tenure_months': tenure, 'income': income, 'age': age}, n, total, flagged)
        store.hset(_online_key(party_id), feats)
        store.hset(_attrs_key(party_id), {'domain': domain, 'journey_stage': stage, 'region': region, 'currency': currency, 'age': age, 'balance': balance, 'risk_band': risk_band, 'consent_ref': consent_ref, 'consent_marketing': consent_mkt, 'fairness_group': fairness_group})
        for name, value in feats.items():
            offline_rows.append((party_id, name, value, now))
    db.execute('DELETE FROM feature_offline')
    db.executemany('INSERT INTO feature_offline (party_id, fname, fvalue, computed_ts) VALUES (?,?,?,?)', offline_rows)
    return len(parties)

def get_online_features(party_id: str) -> dict[str, float]:
    store = db.get_online_store()
    raw = store.hgetall(_online_key(party_id))
    if raw:
        return {k: float(v) for k, v in raw.items()}
    row = db.fetchone('SELECT balance, tenure_months, income, age FROM party WHERE party_id = ?', (party_id,))
    if not row:
        return {name: 0.0 for name in FEATURES}
    feats = compute_offline(party_id, {'balance': row[0], 'tenure_months': row[1], 'income': row[2], 'age': row[3]})
    store.hset(_online_key(party_id), feats)
    return feats

def get_online_attrs(party_id: str) -> dict:
    store = db.get_online_store()
    raw = store.hgetall(_attrs_key(party_id))
    if not raw:
        row = db.fetchone('SELECT domain, journey_stage, region, currency, age, balance, risk_band, consent_ref, consent_marketing, fairness_group FROM party WHERE party_id = ?', (party_id,))
        if not row:
            return {}
        raw = dict(zip(ATTR_COLS, row))
        store.hset(_attrs_key(party_id), raw)
    out = dict(raw)
    for k in ('age', 'balance', 'consent_marketing'):
        if k in out:
            out[k] = float(out[k])
    return out

def feature_vector(party_id: str) -> list[float]:
    feats = get_online_features(party_id)
    return [feats.get(name, 0.0) for name in FEATURES]
if __name__ == '__main__':
    t0 = time.time()
    n = materialize()
    print(f'materialized {n} parties in {time.time() - t0:.1f}s')
    sample = db.fetchone('SELECT party_id FROM party LIMIT 1')[0]
    t1 = time.perf_counter()
    fv = get_online_features(sample)
    print(f'online read {sample} in {(time.perf_counter() - t1) * 1000:.3f}ms -> {fv}')
