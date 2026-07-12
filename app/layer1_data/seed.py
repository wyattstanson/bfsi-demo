"""Layer 1 — Data Foundation: synthetic BFSI personas into the ledger.

Generates parties across the five domains and six journey stages, with accounts,
transactions and consent flags.  PII (name/email/ssn) is stored here in the
system of record and is *never* placed on the hot path or in a model payload.

# PROD: this synthetic generator is replaced by real CDC from core systems.
"""
from __future__ import annotations

import random
import time

from faker import Faker

from app import config
from app.layer1_data import db

fake = Faker()
Faker.seed(42)
random.seed(42)

_RISK = ["low", "medium", "high"]


def _make_party(i: int) -> tuple:
    domain = random.choice(config.DOMAINS)
    stage = random.choice(config.JOURNEY_STAGES)
    age = random.randint(21, 78)
    income = round(random.lognormvariate(11, 0.5), 2)          # ~ ₹/$ annual
    balance = round(max(0.0, random.lognormvariate(9, 1.2)), 2)
    tenure = random.randint(0, 240)
    return (
        f"P{i:06d}",
        domain,
        stage,
        fake.name(),                 # PII
        fake.email(),                # PII
        fake.ssn(),                  # PII
        age,
        income,
        balance,
        tenure,
        random.choice(_RISK),
        random.choice(config.FAIRNESS_GROUPS),
        f"consent-{i:06d}",
        1 if random.random() < 0.7 else 0,
    )


def _make_txns(party_id: str, n: int) -> list[tuple]:
    now = time.time()
    rows = []
    for _ in range(n):
        amount = round(random.lognormvariate(3.5, 1.0), 2)
        # A small, deterministic fraction of transactions are flagged.
        flagged = 1 if random.random() < 0.03 else 0
        rows.append(
            (
                party_id,
                now - random.uniform(0, 90 * 86400),   # within last 90 days
                amount,
                random.choice(["5411", "6011", "4829", "5812", "6300"]),
                random.choice(config.CHANNELS),
                flagged,
            )
        )
    return rows


def seed(n_parties: int | None = None) -> dict:
    n_parties = n_parties or config.SEED_PARTIES
    db.init_schema()
    # Idempotent: skip if already seeded to the requested size.
    existing = db.fetchone("SELECT COUNT(*) FROM party")
    if existing and existing[0] >= n_parties:
        return {"parties": existing[0], "skipped": True}

    db.execute("DELETE FROM txn")
    db.execute("DELETE FROM party")

    parties = [_make_party(i) for i in range(n_parties)]
    db.executemany(
        """INSERT INTO party
           (party_id, domain, journey_stage, name, email, ssn, age, income,
            balance, tenure_months, risk_band, fairness_group, consent_ref,
            consent_marketing)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        parties,
    )

    txns: list[tuple] = []
    for p in parties:
        txns.extend(_make_txns(p[0], random.randint(3, 40)))
    db.executemany(
        "INSERT INTO txn (party_id, ts, amount, mcc, channel, is_flagged) "
        "VALUES (?,?,?,?,?,?)",
        txns,
    )
    return {"parties": len(parties), "txns": len(txns), "skipped": False}


if __name__ == "__main__":
    t0 = time.time()
    result = seed()
    print(f"seeded {result} in {time.time() - t0:.1f}s  backends={db.backends()}")
