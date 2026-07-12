"""Agentic layer — an MCP-style tool registry.

Tools are the only way the agent touches the world.  Two rules enforce safety:
  1. The agent passes **ids**, never PII.  Tools resolve PII server-side and
     return only the minimum, non-PII result (a score, a boolean, a status).
  2. Every tool is registered with metadata so it could be exposed over a real
     MCP server unchanged.

# PROD: swap these mocks for a real MCP server fronting core banking / bureau /
#       sanctions / ledger systems.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Callable

from app.layer1_data import db

# Fields that must never appear in a model/LLM payload.
PII_FIELDS = {"name", "email", "ssn", "phone", "address", "dob"}

_REGISTRY: dict[str, dict[str, Any]] = {}


def tool(name: str, description: str):
    def deco(fn: Callable):
        _REGISTRY[name] = {"fn": fn, "description": description}
        return fn

    return deco


def _deterministic_int(party_id: str, salt: str) -> int:
    return int(hashlib.md5((party_id + salt).encode()).hexdigest(), 16)


@tool("get_customer_profile", "Non-PII operational profile for a party id.")
def get_customer_profile(party_id: str) -> dict:
    row = db.fetchone(
        "SELECT domain, journey_stage, risk_band, tenure_months, consent_marketing "
        "FROM party WHERE party_id = ?",
        (party_id,),
    )
    if not row:
        return {"party_id": party_id, "found": False}
    # PII (name/email/ssn) is deliberately NOT returned.
    return {
        "party_id": party_id,
        "found": True,
        "domain": row[0],
        "journey_stage": row[1],
        "risk_band": row[2],
        "tenure_months": row[3],
        "has_marketing_consent": bool(row[4]),
    }


@tool("get_bureau_score", "Credit bureau score (300-900) for a party id.")
def get_bureau_score(party_id: str) -> dict:
    score = 300 + _deterministic_int(party_id, "bureau") % 601
    return {"party_id": party_id, "bureau_score": score,
            "band": "prime" if score >= 700 else "subprime"}


@tool("check_sanctions", "Screen a party against sanctions/PEP lists (boolean only).")
def check_sanctions(party_id: str) -> dict:
    # Name is resolved server-side for screening but never returned to the model.
    _name = db.fetchone("SELECT name FROM party WHERE party_id = ?", (party_id,))
    hit = _deterministic_int(party_id, "ofac") % 100 < 4  # ~4% deterministic hits
    return {"party_id": party_id, "sanctions_hit": hit}


@tool("post_ledger_entry", "Post a (mocked) ledger entry; returns a reference.")
def post_ledger_entry(party_id: str, amount: float, memo: str) -> dict:
    ref = f"LGR-{_deterministic_int(party_id, memo) % 10**8:08d}"
    return {"party_id": party_id, "posted": True, "amount": amount,
            "ref": ref, "ts": time.time()}


def call(name: str, **kwargs) -> dict:
    if name not in _REGISTRY:
        raise KeyError(f"unknown tool: {name}")
    return _REGISTRY[name]["fn"](**kwargs)


def manifest() -> list[dict]:
    return [{"name": n, "description": m["description"]} for n, m in _REGISTRY.items()]


def assert_no_pii(payload: dict) -> None:
    """Guardrail used before anything is sent to the model/LLM."""
    def scan(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k.lower() in PII_FIELDS:
                    raise ValueError(f"PII field '{k}' must not reach the model")
                scan(v)
        elif isinstance(obj, list):
            for v in obj:
                scan(v)

    scan(payload)
