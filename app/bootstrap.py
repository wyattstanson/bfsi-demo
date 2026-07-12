"""One-shot, idempotent bootstrap: schema → seed → features → models → policies.

Called on server startup and by scripts/bootstrap.py.  Safe to run repeatedly:
each stage is skipped if its output already exists, so warm boots are instant.
"""
from __future__ import annotations

import time

from app import config
from app.agent import memory
from app.layer1_data import db, seed
from app.layer2_features import feature_store
from app.layer3_models import train


def ensure(n_parties: int | None = None, verbose: bool = False) -> dict:
    status = {}
    db.init_schema()

    n = (db.fetchone("SELECT COUNT(*) FROM party") or [0])[0]
    if n == 0:
        seed.seed(n_parties or config.SEED_PARTIES)
        status["seeded"] = True
    status["parties"] = (db.fetchone("SELECT COUNT(*) FROM party") or [0])[0]

    f = (db.fetchone("SELECT COUNT(*) FROM feature_offline") or [0])[0]
    if f == 0:
        feature_store.materialize()
        status["materialized"] = True

    if not (config.ARTIFACTS_DIR / "propensity.pkl").exists():
        status["trained"] = train.train()

    memory.seed_policies()
    status["backends"] = db.backends()
    if verbose:
        print(status)
    return status


if __name__ == "__main__":
    t0 = time.time()
    ensure(verbose=True)
    print(f"bootstrap complete in {time.time() - t0:.1f}s")
