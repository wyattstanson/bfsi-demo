"""Layer 4 — Decisioning: the real-time next-best-action engine.

The hot path for /decide, in order:
  1. pull online features + non-PII attributes (Layer 2, sub-ms)
  2. score every model once (Layer 3)
  3. filter the action catalog by eligibility + do-no-harm rules
  4. rank survivors by expected value, with a LinUCB exploration bonus
  5. return the winner plus every intermediate number (for Layer 5 to explain)

Everything is loaded once at startup so warm calls stay well under the SLO.
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import yaml

from app.layer2_features import feature_store
from app.layer3_models.fraud import FraudModel
from app.layer3_models.propensity import BinaryModel
from app.layer3_models.uplift import UpliftModel
from app.layer4_decisioning.bandit import LinUCB

_CATALOG = Path(__file__).parent / "action_catalog.yaml"


class Decision(dict):
    """A plain dict; named for readability at call sites."""


class DecisionEngine:
    def __init__(self) -> None:
        self.propensity = BinaryModel.load("propensity")
        self.churn = BinaryModel.load("churn")
        self.uplift = UpliftModel.load()
        self.fraud = FraudModel.load()
        with open(_CATALOG) as f:
            self.actions = yaml.safe_load(f)["actions"]
        self.bandit = LinUCB(dim=5, alpha=0.5)
        self.baseline = self._population_baseline()
        self.model_versions = {
            "propensity": self.propensity.version,
            "churn": self.churn.version,
            "uplift": self.uplift.version,
            "fraud": self.fraud.version,
        }

    def _population_baseline(self) -> list[float]:
        """Mean feature vector — the reference point for SHAP-style attribution."""
        from app.layer1_data import db

        vals = {f: [] for f in feature_store.FEATURES}
        for fname, fval in db.fetchall("SELECT fname, fvalue FROM feature_offline"):
            if fname in vals:
                vals[fname].append(fval)
        return [float(np.mean(v)) if v else 0.0 for v in vals.values()]

    def signal_predict(self, signal: str, vec: list[float]) -> float:
        """Uniform scoring interface used by governance's attribution."""
        if signal == "propensity":
            return self.propensity.predict_proba(vec)
        if signal == "churn":
            return self.churn.predict_proba(vec)
        if signal == "uplift":
            return max(0.0, self.uplift.uplift(vec))
        return 0.0  # fraud is graph-based; explained separately

    # ---- eligibility + guardrails ---------------------------------------
    @staticmethod
    def _eligible(action: dict, attrs: dict, scores: dict) -> tuple[bool, str]:
        el = action.get("eligibility", {})
        if attrs.get("age", 0) < el.get("min_age", 0):
            return False, "age_below_min"
        if el.get("requires_consent_marketing") and not attrs.get("consent_marketing"):
            return False, "no_marketing_consent"
        if attrs.get("balance", 0) < el.get("min_balance", 0):
            return False, "balance_below_min"
        dnh = action.get("do_no_harm", {})
        if "max_churn" in dnh and scores["churn"] > dnh["max_churn"]:
            return False, "do_no_harm_churn"
        if "max_fraud" in dnh and scores["fraud"] > dnh["max_fraud"]:
            return False, "do_no_harm_fraud"
        return True, "eligible"

    def decide(self, party_id: str, event: dict | None = None) -> Decision:
        event = event or {}
        vec = feature_store.feature_vector(party_id)
        attrs = feature_store.get_online_attrs(party_id)
        feats = dict(zip(feature_store.FEATURES, vec))

        scores = {
            "propensity": self.propensity.predict_proba(vec),
            "churn": self.churn.predict_proba(vec),
            "uplift": self.uplift.uplift(vec),
            "fraud": self.fraud.score(
                party_id, feats["payments__party__flagged_ratio__90d"], event
            ),
        }
        # Bandit context: the four model signals + bias, all bounded.
        ctx = np.array(
            [scores["propensity"], scores["churn"], max(scores["uplift"], 0.0),
             scores["fraud"], 1.0]
        )

        ranked, rejected = [], []
        for a in self.actions:
            ok, reason = self._eligible(a, attrs, scores)
            if not ok:
                rejected.append({"action_id": a["id"], "reason": reason})
                continue
            signal_value = max(0.0, scores[a["signal"]])
            expected_value = a["base_value"] * signal_value
            explore = self.bandit.score(a["id"], ctx)
            rank_score = expected_value + 0.5 * explore
            ranked.append(
                {
                    "action_id": a["id"],
                    "action": a,
                    "signal": a["signal"],
                    "signal_value": round(signal_value, 4),
                    "expected_value": round(expected_value, 2),
                    "rank_score": round(rank_score, 4),
                }
            )

        ranked.sort(key=lambda r: r["rank_score"], reverse=True)
        winner = ranked[0]
        return Decision(
            party_id=party_id,
            event=event,
            winner=winner,
            ranked=ranked,
            rejected=rejected,
            model_scores=scores,
            features_snapshot=feats,
            attrs=attrs,
            model_versions=self.model_versions,
        )

    def reward(self, party_id: str, action_id: str, ctx: list[float], reward: float) -> None:
        """Feed a realized outcome back to the bandit (online learning)."""
        self.bandit.update(action_id, np.asarray(ctx, dtype=float), reward)


_engine: DecisionEngine | None = None


def get_engine() -> DecisionEngine:
    global _engine
    if _engine is None:
        _engine = DecisionEngine()
    return _engine


if __name__ == "__main__":
    from app.layer1_data import db

    eng = get_engine()
    pid = db.fetchone("SELECT party_id FROM party LIMIT 1")[0]
    t0 = time.perf_counter()
    d = eng.decide(pid, {"event_type": "large_transfer_attempt", "amount": 4000})
    dt = (time.perf_counter() - t0) * 1000
    print(f"{pid} -> {d['winner']['action_id']}  ev={d['winner']['expected_value']} "
          f"in {dt:.2f}ms")
    print("scores:", {k: round(v, 3) for k, v in d["model_scores"].items()})
