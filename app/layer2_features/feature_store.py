"""Layer 2 — Feature Store: one definition, two serving paths.

  * Offline (batch): compute features from the ledger and persist them, both to
    the ledger `feature_offline` table and warmed into the online store.
  * Online (hot path): `get_online_features(party_id)` reads the online store by
    key in sub-millisecond time — this is what /decide calls.

Naming convention is enforced: every feature key is `domain__entity__metric__window`.
Consistency between the two paths is the entire reason a feature store exists
(no train/serve skew).

# PROD: swap for Feast / Databricks Feature Store + Tecton-style online serving.
"""
from __future__ import annotations

import re
import time

from app.layer1_data import db

# Each of the four segments may contain single underscores (e.g. metric
# "txn_amount_sum"); the segments themselves are separated by a double underscore.
_SEG = re.compile(r"^[a-z0-9]+(_[a-z0-9]+)*$")


def _validate(name: str) -> str:
    parts = name.split("__")
    if len(parts) != 4 or not all(_SEG.match(p) for p in parts):
        raise ValueError(
            f"feature '{name}' violates domain__entity__metric__window convention"
        )
    return name


# The offline feature definitions.  Each returns a float from ledger rows.
# Keyed by the enforced naming convention.
FEATURES = [
    "retail__party__txn_count__90d",
    "retail__party__txn_amount_sum__90d",
    "retail__party__txn_amount_avg__90d",
    "payments__party__flagged_ratio__90d",
    "wealth__party__balance__now",
    "nbfc__party__tenure__months",
    "retail__party__income__now",
    "retail__party__age__now",
]
for _f in FEATURES:
    _validate(_f)


def _online_key(party_id: str) -> str:
    return f"features:{party_id}"


def _attrs_key(party_id: str) -> str:
    return f"attrs:{party_id}"


# Non-PII eligibility attributes served on the hot path alongside features.
# Deliberately excludes name/email/ssn — those stay in the ledger only.
ATTR_COLS = [
    "domain",
    "journey_stage",
    "age",
    "balance",
    "risk_band",
    "consent_ref",
    "consent_marketing",
    "fairness_group",  # audit-only; carried for Layer 5, never used for scoring
]


def compute_offline(party_id: str, row: dict) -> dict[str, float]:
    """Compute the feature vector for one party from ledger aggregates."""
    txns = db.fetchall(
        "SELECT amount, is_flagged FROM txn WHERE party_id = ?", (party_id,)
    )
    n = len(txns)
    total = sum(a for a, _ in txns)
    flagged = sum(f for _, f in txns)
    return {
        "retail__party__txn_count__90d": float(n),
        "retail__party__txn_amount_sum__90d": round(total, 2),
        "retail__party__txn_amount_avg__90d": round(total / n, 2) if n else 0.0,
        "payments__party__flagged_ratio__90d": round(flagged / n, 4) if n else 0.0,
        "wealth__party__balance__now": float(row["balance"]),
        "nbfc__party__tenure__months": float(row["tenure_months"]),
        "retail__party__income__now": float(row["income"]),
        "retail__party__age__now": float(row["age"]),
    }


def materialize(limit: int | None = None) -> int:
    """Batch job: compute all parties' features, persist offline + warm online."""
    cols = ("party_id, balance, tenure_months, income, age, domain, journey_stage, "
            "risk_band, consent_ref, consent_marketing, fairness_group")
    sql = f"SELECT {cols} FROM party"
    if limit:
        sql += f" LIMIT {int(limit)}"
    parties = db.fetchall(sql)
    store = db.get_online_store()
    now = time.time()
    offline_rows = []
    for (party_id, balance, tenure, income, age, domain, stage, risk_band,
         consent_ref, consent_mkt, fairness_group) in parties:
        feats = compute_offline(
            party_id,
            {"balance": balance, "tenure_months": tenure, "income": income, "age": age},
        )
        # Warm the online store (hot path): features + non-PII attributes.
        store.hset(_online_key(party_id), feats)
        store.hset(
            _attrs_key(party_id),
            {
                "domain": domain,
                "journey_stage": stage,
                "age": age,
                "balance": balance,
                "risk_band": risk_band,
                "consent_ref": consent_ref,
                "consent_marketing": consent_mkt,
                "fairness_group": fairness_group,
            },
        )
        for name, value in feats.items():
            offline_rows.append((party_id, name, value, now))

    # Persist offline copy for training / lineage (upsert).
    db.execute("DELETE FROM feature_offline")
    db.executemany(
        "INSERT INTO feature_offline (party_id, fname, fvalue, computed_ts) "
        "VALUES (?,?,?,?)",
        offline_rows,
    )
    return len(parties)


def get_online_features(party_id: str) -> dict[str, float]:
    """Hot-path read.  Sub-millisecond: a single online-store hash lookup.

    Falls back to on-the-fly compute if the party was never materialized
    (keeps the demo robust; in prod this would be a cache miss + async backfill).
    """
    store = db.get_online_store()
    raw = store.hgetall(_online_key(party_id))
    if raw:
        return {k: float(v) for k, v in raw.items()}
    # Cache miss — compute from ledger and warm the key.
    row = db.fetchone(
        "SELECT balance, tenure_months, income, age FROM party WHERE party_id = ?",
        (party_id,),
    )
    if not row:
        return {name: 0.0 for name in FEATURES}
    feats = compute_offline(
        party_id,
        {"balance": row[0], "tenure_months": row[1], "income": row[2], "age": row[3]},
    )
    store.hset(_online_key(party_id), feats)
    return feats


def get_online_attrs(party_id: str) -> dict:
    """Hot-path read of non-PII eligibility attributes."""
    store = db.get_online_store()
    raw = store.hgetall(_attrs_key(party_id))
    if not raw:
        row = db.fetchone(
            "SELECT domain, journey_stage, age, balance, risk_band, consent_ref, "
            "consent_marketing, fairness_group FROM party WHERE party_id = ?",
            (party_id,),
        )
        if not row:
            return {}
        raw = dict(zip(ATTR_COLS, row))
        store.hset(_attrs_key(party_id), raw)
    # Coerce numeric-ish fields.
    out = dict(raw)
    for k in ("age", "balance", "consent_marketing"):
        if k in out:
            out[k] = float(out[k])
    return out


def feature_vector(party_id: str) -> list[float]:
    """Ordered vector (stable column order) for model scoring."""
    feats = get_online_features(party_id)
    return [feats.get(name, 0.0) for name in FEATURES]


if __name__ == "__main__":
    t0 = time.time()
    n = materialize()
    print(f"materialized {n} parties in {time.time() - t0:.1f}s")
    sample = db.fetchone("SELECT party_id FROM party LIMIT 1")[0]
    t1 = time.perf_counter()
    fv = get_online_features(sample)
    print(f"online read {sample} in {(time.perf_counter() - t1) * 1000:.3f}ms -> {fv}")
