"""FastAPI application — the seam that ties all five layers + the agent together.

Routes:
  GET  /                 the minimal demo frontend
  POST /decide           Layer 4 decision + Layer 5 governance, under the SLO
  POST /agent            the agentic loop, streamed as Server-Sent Events
  GET  /personas         non-PII sample parties for the frontend picker
  GET  /audit/{id}       fetch one audit row
  GET  /governance       drift + fairness snapshots
  GET  /health           backends + row counts
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from app import bootstrap, config
from app.agent import agent
from app.layer1_data import db
from app.layer4_decisioning.decisioning import get_engine
from app.layer5_governance import audit, fairness, governance

_STATIC = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    bootstrap.ensure()
    get_engine()  # load models + warm the engine so the first /decide is warm
    yield


app = FastAPI(title="BFSI structural personalization demo", lifespan=lifespan)


class DecideRequest(BaseModel):
    party_id: str
    event: dict | None = None
    channel: str = "app"


class AgentRequest(BaseModel):
    party_id: str
    goal: str


@app.get("/")
def index():
    return FileResponse(_STATIC / "index.html")


@app.post("/decide")
def decide(req: DecideRequest):
    """Return a personalized next-best-action with full governance, under SLO.

    Latency is measured across the entire hot path *including* the SHAP-style
    explanation and fairness flag — governance is not free, so it counts.
    """
    engine = get_engine()
    t0 = time.perf_counter()
    decision = engine.decide(req.party_id, req.event)
    assessment = governance.assess(engine, decision)
    latency_ms = (time.perf_counter() - t0) * 1000.0
    record = governance.build_record(decision, assessment, req.channel, latency_ms)
    audit.write(record)  # exactly one audit row per decision

    winner = decision["winner"]
    return {
        "decision_id": record["decision_id"],
        "action": winner["action_id"],
        "action_detail": winner["action"],
        "score": winner["expected_value"],
        "reason_codes": record["reason_codes"],
        "fairness_flag": record["fairness_flag"],
        "latency_ms": round(latency_ms, 3),
        "slo_ms": config.LATENCY_SLO_MS,
        "within_slo": latency_ms < config.LATENCY_SLO_MS,
        "model_scores": {k: round(v, 4) for k, v in decision["model_scores"].items()},
        "model_versions": decision["model_versions"],
        "ranked": [
            {"action_id": r["action_id"], "expected_value": r["expected_value"],
             "signal": r["signal"], "signal_value": r["signal_value"]}
            for r in decision["ranked"]
        ],
        "rejected": decision["rejected"],
    }


@app.post("/agent")
def run_agent(req: AgentRequest):
    """Stream the perceive→reason→act→observe loop as SSE."""

    def gen():
        for ev in agent.run_stream(req.party_id, req.goal):
            yield f"data: {json.dumps(ev)}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.get("/personas")
def personas(limit: int = 12):
    rows = db.fetchall(
        "SELECT party_id, domain, journey_stage, risk_band FROM party LIMIT ?",
        (limit,),
    )
    # Non-PII only.
    return [
        {"party_id": p, "domain": d, "journey_stage": s, "risk_band": r}
        for p, d, s, r in rows
    ]


@app.get("/audit/{decision_id}")
def get_audit(decision_id: str):
    row = audit.get(decision_id)
    return row or {"error": "not found"}


@app.get("/governance")
def governance_snapshot():
    return {
        "drift": governance.drift_snapshot(),
        "fairness": fairness.snapshot(),
        "audit_rows": audit.count(),
        "human_queue": (db.fetchone("SELECT COUNT(*) FROM human_queue") or [0])[0],
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "backends": db.backends(),
        "parties": (db.fetchone("SELECT COUNT(*) FROM party") or [0])[0],
        "audit_rows": audit.count(),
        "agent_engine": "langgraph" if agent._HAS_LANGGRAPH else "hand-rolled",
    }
