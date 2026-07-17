from __future__ import annotations
import time
import numpy as np
from app.layer1_data import db
from app.layer2_features import feature_store
from app.layer3_models.fraud import FraudModel
from app.layer3_models.propensity import BinaryModel
from app.layer3_models.uplift import UpliftModel
VERSION = time.strftime('v%Y%m%d.%H%M%S')

def _matrix() -> tuple[list[str], np.ndarray]:
    rows = db.fetchall('SELECT party_id, fname, fvalue FROM feature_offline')
    if not rows:
        raise RuntimeError('no features materialized — run feature_store first')
    by_party: dict[str, dict[str, float]] = {}
    for pid, fname, fval in rows:
        by_party.setdefault(pid, {})[fname] = fval
    ids = sorted(by_party)
    X = np.array([[by_party[p].get(f, 0.0) for f in feature_store.FEATURES] for p in ids], dtype=float)
    return (ids, X)

def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))

def _labels(X: np.ndarray, rng: np.random.Generator):
    txn_count, _sum, _avg, flagged, balance, tenure, income, age = X.T
    z_prop = 1e-05 * balance + 2e-05 * income + 0.03 * txn_count - 4.0
    y_prop = (rng.random(len(X)) < _sigmoid(z_prop)).astype(int)
    z_churn = 3.0 * flagged - 0.01 * tenure - 0.02 * txn_count + 0.5
    y_churn = (rng.random(len(X)) < _sigmoid(z_churn)).astype(int)
    T = (rng.random(len(X)) < 0.5).astype(int)
    effect = 0.25 * np.exp(-(tenure - 60) ** 2 / (2 * 40 ** 2))
    z_base = 1e-05 * income - 1.0
    p_out = _sigmoid(z_base + T * effect * 6.0)
    Y = (rng.random(len(X)) < p_out).astype(int)
    return (y_prop, y_churn, T, Y)

def train() -> dict:
    rng = np.random.default_rng(7)
    ids, X = _matrix()
    y_prop, y_churn, T, Y = _labels(X, rng)
    propensity = BinaryModel('propensity', VERSION).fit(X, y_prop)
    churn = BinaryModel('churn', VERSION).fit(X, y_churn)
    uplift = UpliftModel(VERSION).fit(X, T, Y)
    txns = db.fetchall('SELECT party_id, mcc, is_flagged FROM txn')
    fraud = FraudModel(VERSION).fit(txns)
    for m in (propensity, churn, uplift, fraud):
        m.save()
    return {'version': VERSION, 'n': len(ids), 'algos': {'propensity': propensity.algo, 'churn': churn.algo, 'uplift': uplift.algo, 'fraud': fraud.algo}, 'positives': {'propensity': int(y_prop.sum()), 'churn': int(y_churn.sum())}}
if __name__ == '__main__':
    t0 = time.time()
    print(train(), f'in {time.time() - t0:.1f}s')
