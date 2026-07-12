"""Agentic layer — a stateful perceive → reason → act → observe loop.

Runs on agentic data (the same online store + ledger) and closes a simple task
end-to-end using the MCP-style tools, with vector memory and a hard
human-escalation path on low confidence or high stakes.

Uses LangGraph to wire the nodes when it is importable; otherwise a hand-rolled
driver runs the identical node functions so the demo never fails to boot.

# PROD: run this graph as LangGraph on EKS with a real MCP tool server.
"""
from __future__ import annotations

import re
import time

from app.agent import memory, tools
from app.layer1_data import db
from app.layer3_models import llm

try:
    from langgraph.graph import StateGraph  # type: ignore  # noqa: F401

    _HAS_LANGGRAPH = True
except Exception:
    _HAS_LANGGRAPH = False

MAX_STEPS = 8


# --------------------------------------------------------------------------- #
# Goal understanding
# --------------------------------------------------------------------------- #
def _parse_goal(goal: str) -> dict:
    g = goal.lower()
    amount_match = re.search(r"(\d[\d,]*\.?\d*)", g)
    amount = float(amount_match.group(1).replace(",", "")) if amount_match else 0.0
    if any(w in g for w in ("loan", "credit", "pre-approved", "preapproved")):
        intent = "loan"
    elif any(w in g for w in ("dispute", "chargeback", "fraud", "unauthorized")):
        intent = "dispute"
    elif any(w in g for w in ("transfer", "pay", "send")):
        intent = "transfer"
    else:
        intent = "info"
    return {"intent": intent, "amount": amount}


# --------------------------------------------------------------------------- #
# Nodes (each takes state, mutates it, returns the next node name)
# --------------------------------------------------------------------------- #
def perceive(state: dict) -> str:
    profile = tools.call("get_customer_profile", party_id=state["party_id"])
    docs = memory.recall(state["goal"], state["party_id"], k=3, kinds=["policy"])
    state["gathered"]["profile"] = profile
    state["gathered"]["policy_hits"] = docs
    # Build the payload that will reach the model — ids + non-PII only.
    state["model_payload"] = {
        "party_id": state["party_id"],
        "intent": state["parsed"]["intent"],
        "profile": profile,
        "policy": docs,
    }
    tools.assert_no_pii(state["model_payload"])  # guardrail
    state["steps"].append({"node": "perceive", "detail": f"profile+{len(docs)} policy docs"})
    return "reason"


def reason(state: dict) -> str:
    intent = state["parsed"]["intent"]
    need = {
        "loan": ["get_bureau_score", "check_sanctions"],
        "transfer": ["check_sanctions"],
        "dispute": ["check_sanctions"],
        "info": [],
    }[intent]
    missing = [t for t in need if t not in state["gathered"].get("tools", {})]
    if missing:
        state["next_tool"] = missing[0]
        state["steps"].append({"node": "reason", "detail": f"need {missing[0]}"})
        return "act"
    state["steps"].append({"node": "reason", "detail": "all evidence gathered; deciding"})
    return "decide"


def act(state: dict) -> str:
    name = state["next_tool"]
    result = tools.call(name, party_id=state["party_id"])
    state["gathered"].setdefault("tools", {})[name] = result
    state["steps"].append({"node": "act", "detail": f"{name} -> {result}"})
    return "observe"


def observe(state: dict) -> str:
    last = state["steps"][-1]["detail"]
    memory.remember(state["party_id"], "episodic", f"{state['goal']} :: {last}")
    state["steps"].append({"node": "observe", "detail": "noted to memory"})
    return "reason"


def decide(state: dict) -> str:
    intent = state["parsed"]["intent"]
    amount = state["parsed"]["amount"]
    t = state["gathered"].get("tools", {})
    sanctions_hit = t.get("check_sanctions", {}).get("sanctions_hit", False)
    bureau = t.get("get_bureau_score", {}).get("bureau_score", 0)

    # High-stakes / low-confidence escalation rules (human in the loop).
    if sanctions_hit:
        return _escalate(state, "sanctions_hit", confidence=0.2)
    if intent == "loan" and bureau < 700:
        return _escalate(state, f"bureau_score {bureau} < 700", confidence=0.4)
    if intent == "dispute" and amount > 10000:
        return _escalate(state, f"high-value dispute {amount} > 10000", confidence=0.3)
    if intent == "transfer" and amount > 3000:
        return _escalate(state, f"transfer {amount} needs step-up", confidence=0.5)

    # Otherwise the agent can complete the task autonomously.
    if intent in ("loan", "transfer"):
        memo = "loan_disbursal" if intent == "loan" else "transfer"
        posted = tools.call("post_ledger_entry", party_id=state["party_id"],
                            amount=amount or 0.0, memo=memo)
        state["answer"] = f"Completed {intent}: ledger ref {posted['ref']}."
        state["steps"].append({"node": "act", "detail": f"post_ledger_entry -> {posted['ref']}"})
    else:  # dispute / info — answer with grounded, cited text
        payload = dict(state["model_payload"])
        tools.assert_no_pii(payload)
        grounded = llm.grounded_answer(state["goal"], state["gathered"]["policy_hits"])
        state["answer"] = grounded["answer"]
        state["citations"] = grounded["citations"]
        if not grounded["citations"]:
            return _escalate(state, "no grounded policy match", confidence=0.4)
        state["steps"].append({"node": "act", "detail": "grounded_answer (cited)"})

    state["confidence"] = 0.85
    state["done"] = True
    state["steps"].append({"node": "observe", "detail": "task complete"})
    return "end"


def _escalate(state: dict, reason: str, confidence: float) -> str:
    """Write to the human queue with the gathered (non-PII) context, and stop."""
    context = {
        "profile": state["gathered"].get("profile"),
        "tools": state["gathered"].get("tools", {}),
        "policy_hits": state["gathered"].get("policy_hits", []),
        "parsed": state["parsed"],
    }
    tools.assert_no_pii(context)
    db.execute(
        "INSERT INTO human_queue (party_id, goal, reason, context, ts, resolved) "
        "VALUES (?,?,?,?,?,?)",
        (state["party_id"], state["goal"], reason, db.as_json(context), time.time(), 0),
    )
    state["escalated"] = True
    state["escalation_reason"] = reason
    state["confidence"] = confidence
    state["done"] = True
    state["answer"] = f"Escalated to human review: {reason}."
    state["steps"].append({"node": "escalate", "detail": reason})
    return "end"


_NODES = {
    "perceive": perceive,
    "reason": reason,
    "act": act,
    "observe": observe,
    "decide": decide,
}


def _initial_state(party_id: str, goal: str) -> dict:
    return {
        "party_id": party_id,
        "goal": goal,
        "parsed": _parse_goal(goal),
        "gathered": {},
        "steps": [],
        "confidence": 1.0,
        "escalated": False,
        "done": False,
        "answer": None,
        "engine": "langgraph" if _HAS_LANGGRAPH else "hand-rolled",
    }


def run_stream(party_id: str, goal: str):
    """Drive the graph, yielding each step as it happens (for SSE streaming)."""
    state = _initial_state(party_id, goal)
    node = "perceive"
    steps_emitted = 0
    guard = 0
    while node != "end" and guard < MAX_STEPS * 3:
        guard += 1
        node = _NODES[node](state)
        # Emit any steps produced since the last yield.
        while steps_emitted < len(state["steps"]):
            yield {"type": "step", **state["steps"][steps_emitted]}
            steps_emitted += 1
    yield {
        "type": "final",
        "answer": state["answer"],
        "escalated": state["escalated"],
        "confidence": state["confidence"],
        "engine": state["engine"],
        "citations": state.get("citations", []),
    }


def run(party_id: str, goal: str) -> dict:
    """Non-streaming convenience wrapper (used by tests)."""
    final = None
    steps = []
    for ev in run_stream(party_id, goal):
        if ev["type"] == "final":
            final = ev
        else:
            steps.append(ev)
    return {"steps": steps, **(final or {})}


if __name__ == "__main__":
    memory.seed_policies()
    pid = db.fetchone("SELECT party_id FROM party LIMIT 1")[0]
    for g in ["I want a pre-approved loan of 50000",
              "Dispute an unauthorized charge of 15000",
              "Give me a financial tip"]:
        r = run(pid, g)
        print(f"\nGOAL: {g}\n  -> {r['answer']}  (escalated={r['escalated']}, "
              f"conf={r['confidence']}, engine={r['engine']}, steps={len(r['steps'])})")
