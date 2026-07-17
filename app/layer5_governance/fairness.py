from __future__ import annotations
import threading
from collections import defaultdict
_lock = threading.Lock()
_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
VALUABLE = {'retail_cross_sell_credit_card', 'wealth_advisory_upgrade', 'nbfc_preapproved_loan'}
THRESHOLD = 0.8

def observe(fairness_group: str, action_id: str) -> str:
    with _lock:
        c = _counts[fairness_group]
        c[1] += 1
        if action_id in VALUABLE:
            c[0] += 1
        rates = [sel / tot for sel, tot in _counts.values() if tot >= 20]
    if len(rates) < 2:
        return 'insufficient_data'
    hi = max(rates)
    lo = min(rates)
    air = lo / hi if hi > 0 else 1.0
    return 'ok' if air >= THRESHOLD else 'adverse_impact'

def snapshot() -> dict:
    with _lock:
        return {g: {'selected': c[0], 'total': c[1], 'rate': round(c[0] / c[1], 3) if c[1] else 0.0} for g, c in _counts.items()}
