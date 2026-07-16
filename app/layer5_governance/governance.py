"""Layer 5 — Governance: make every decision a *regulated* decision.

`finalize()` is the single choke point through which all decisions pass. It:
  * produces SHAP-style reason codes (baseline attribution, model-agnostic),
  * attaches a fairness flag (Layer 5 fairness.py),
  * updates drift counters,
  * writes the one append-only audit row,
and only then hands the record back for the API response.

# PROD: swap the local SHAP approximation for the `shap` library on a served
#       model, and the counters for a monitored drift service.
"""
from __future__ import annotations

import threading

from app.layer5_governance import audit, fairness

# Human-readable labels for reason codes.
LABELS = {
    "retail__party__txn_count__90d": "transaction frequency (90d)",
    "retail__party__txn_amount_sum__90d": "total spend (90d)",
    "retail__party__txn_amount_avg__90d": "average ticket size (90d)",
    "payments__party__flagged_ratio__90d": "flagged-transaction ratio (90d)",
    "wealth__party__balance__now": "current balance",
    "nbfc__party__tenure__months": "tenure (months)",
    "retail__party__income__now": "income",
    "retail__party__age__now": "age",
}

# ---- drift monitoring (running mean of each model signal) -------------------
_lock = threading.Lock()
_drift = {k: {"n": 0, "sum": 0.0, "alerts": 0} for k in
          ("propensity", "churn", "uplift", "fraud")}
_DRIFT_HI = {"propensity": 0.9, "churn": 0.9, "uplift": 0.9, "fraud": 0.9}


def _update_drift(scores: dict) -> None:
    with _lock:
        for k, v in scores.items():
            d = _drift[k]
            d["n"] += 1
            d["sum"] += v
            if v > _DRIFT_HI[k]:
                d["alerts"] += 1


def drift_snapshot() -> dict:
    with _lock:
        return {
            k: {"mean": round(d["sum"] / d["n"], 4) if d["n"] else 0.0,
                "alerts": d["alerts"], "n": d["n"]}
            for k, d in _drift.items()
        }


def shap_reasons(engine, decision: dict, top_k: int = 3) -> list[dict]:
    """Baseline (Shapley-flavoured) attribution for the winning action.

    For each feature, measure how much the winning signal changes when that
    feature is reset to the population baseline: a model-agnostic, per-decision
    explanation that works for logistic, XGBoost, or T-learner alike.
    """
    from app.layer2_features import feature_store

    winner = decision["winner"]
    signal = winner["signal"]

    # Fraud is a graph score, not a feature-vector model — explain it directly.
    if signal == "fraud":
        feats = decision["features_snapshot"]
        reasons = [
            {
                "feature": "payments__party__flagged_ratio__90d",
                "label": LABELS["payments__party__flagged_ratio__90d"],
                "value": round(feats["payments__party__flagged_ratio__90d"], 4),
                "contribution": round(decision["model_scores"]["fraud"], 4),
                "direction": "increases",
            }
        ]
        if decision.get("event", {}).get("event_type") == "large_transfer_attempt":
            reasons.append(
                {
                    "feature": "live__event__large_transfer__now",
                    "label": "live large-transfer attempt",
                    "value": decision["event"].get("amount", 0.0),
                    "contribution": 0.4,
                    "direction": "increases",
                }
            )
        return reasons

    vec = [decision["features_snapshot"][f] for f in feature_store.FEATURES]

    exact = engine.signal_contributions(signal, vec)
    if exact is not None:
        # Linear model: contributions are exact and need no extra model calls.
        contribs = [(fname, exact[i], vec[i])
                    for i, fname in enumerate(feature_store.FEATURES)]
    else:
        # Tree model: fall back to baseline perturbation attribution.
        base = engine.baseline
        f_full = engine.signal_predict(signal, vec)
        contribs = []
        for i, fname in enumerate(feature_store.FEATURES):
            perturbed = list(vec)
            perturbed[i] = base[i]
            delta = f_full - engine.signal_predict(signal, perturbed)
            contribs.append((fname, delta, vec[i]))

    contribs.sort(key=lambda c: abs(c[1]), reverse=True)
    return [
        {
            "feature": fname,
            "label": LABELS.get(fname, fname),
            "value": round(val, 4),
            "contribution": round(delta, 4),
            "direction": "increases" if delta >= 0 else "decreases",
        }
        for fname, delta, val in contribs[:top_k]
    ]


def assess(engine, decision: dict) -> dict:
    """Explain + flag + monitor (no write).  Kept separate so the API can fold
    this work into the measured latency and still write the audit row once."""
    reason_codes = shap_reasons(engine, decision)
    fairness_flag = fairness.observe(
        decision["attrs"].get("fairness_group", "unknown"),
        decision["winner"]["action_id"],
    )
    _update_drift(decision["model_scores"])
    return {"reason_codes": reason_codes, "fairness_flag": fairness_flag}


def build_record(decision: dict, assessment: dict, channel: str,
                 latency_ms: float, mode: str = "auto") -> dict:
    winner = decision["winner"]
    attrs = decision["attrs"]
    return {
        "decision_id": audit.new_decision_id(),
        "party_id": decision["party_id"],
        "channel": channel,
        "use_case": winner["action"]["use_case"],
        "action_id": winner["action_id"],
        "features_snapshot": decision["features_snapshot"],
        "model_versions": decision["model_versions"],
        "score": winner["expected_value"],
        "reason_codes": assessment["reason_codes"],
        "fairness_flag": assessment["fairness_flag"],
        "mode": mode,
        "latency_ms": round(latency_ms, 3),
        "consent_ref": attrs.get("consent_ref", ""),
        "human_reviewed": 0,
        "override": "",
    }


def finalize(engine, decision: dict, channel: str, latency_ms: float,
             mode: str = "auto") -> dict:
    """The regulated choke point: explain, flag, monitor, audit — then return.

    Convenience for non-HTTP callers; the API path uses assess/build_record so
    governance time is included in the reported latency.
    """
    assessment = assess(engine, decision)
    record = build_record(decision, assessment, channel, latency_ms, mode)
    audit.write(record)   # exactly one row per decision, before we return
    return record
