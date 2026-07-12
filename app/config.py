"""Cross-cutting configuration (paths + environment).

Not a numbered layer — this is shared plumbing. Every module reads settings from
here so that switching a local component for its cloud equivalent is a matter of
setting an environment variable, never editing code.
"""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # dotenv is optional
    pass

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / ".data"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
DATA_DIR.mkdir(exist_ok=True)
ARTIFACTS_DIR.mkdir(exist_ok=True)

# Layer 1 — system of record.  Postgres if DATABASE_URL is set, else local SQLite.
DATABASE_URL = os.getenv("DATABASE_URL", "")
SQLITE_PATH = str(DATA_DIR / "bfsi.db")

# Layer 1/2 — online hot-path store.  Redis if REDIS_URL is set, else in-process.
REDIS_URL = os.getenv("REDIS_URL", "")

# Layer 3 — grounded LLM.  Offline deterministic stub if no key.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-5")

SEED_PARTIES = int(os.getenv("SEED_PARTIES", "10000"))
LATENCY_SLO_MS = float(os.getenv("LATENCY_SLO_MS", "98"))

# Shared BFSI vocabulary (matches the reference jargon sheet).
DOMAINS = ["retail", "wealth", "payments", "nbfc", "insurance"]
JOURNEY_STAGES = ["discover", "originate", "engage", "cross_sell", "service", "retain"]
CHANNELS = ["app", "web", "branch", "call_center", "sms"]
# A protected attribute is carried ONLY for offline fairness auditing, never scored.
FAIRNESS_GROUPS = ["group_a", "group_b"]
