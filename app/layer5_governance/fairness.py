"""Layer 5 — Governance: a fairness signal per decision.

Computes an adverse-impact ratio (a.k.a. the four-fifths rule): the selection
rate of the least-favoured group divided by that of the most-favoured group,
across recent decisions.  A ratio below 0.8 raises a fairness flag.

The protected attribute (`fairness_group`) is used ONLY here for auditing — it is
never a model input.  This is a placeholder metric; a production system would run
a full fairness suite offline.

# PROD: swap for a monitored fairness service (e.g. Fairlearn / model monitor).
"""
from __future__ import annotations

import threading
from collections import defaultdict

_lock = threading.Lock()
# group -> [selected_for_valuable_action, total]
_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])

# Actions considered "valuable" (a benefit being allocated) for the AIR test.
VALUABLE = {
    "retail_cross_sell_credit_card",
    "wealth_advisory_upgrade",
    "nbfc_preapproved_loan",
}
THRESHOLD = 0.8


def observe(fairness_group: str, action_id: str) -> str:
    """Record one decision, return the current fairness flag."""
    with _lock:
        c = _counts[fairness_group]
        c[1] += 1
        if action_id in VALUABLE:
            c[0] += 1
        rates = [
            (sel / tot) for sel, tot in _counts.values() if tot >= 20
        ]
    if len(rates) < 2:
        return "insufficient_data"
    hi = max(rates)
    lo = min(rates)
    air = (lo / hi) if hi > 0 else 1.0
    return "ok" if air >= THRESHOLD else "adverse_impact"


def snapshot() -> dict:
    with _lock:
        return {
            g: {"selected": c[0], "total": c[1], "rate": round(c[0] / c[1], 3) if c[1] else 0.0}
            for g, c in _counts.items()
        }
