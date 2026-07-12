"""Streamlit front-end for the BFSI structural demo — a shareable deploy target.

Streamlit Cloud runs a Streamlit script, not a uvicorn server, so this UI calls
the five-layer logic **in-process** (bootstrap → decide → govern → agent) instead
of going over HTTP. Same engine, same audit trail, same sub-98ms hot path — just
a different presentation layer bolted onto Layer 4/5 and the agent.

Run locally:   streamlit run streamlit_app.py
Deploy:        push to GitHub, then share.streamlit.io → pick repo → main file
               = streamlit_app.py.
"""
from __future__ import annotations

import os
import time

# Keep the cloud instance light (Streamlit Community Cloud ~1GB RAM).
os.environ.setdefault("SEED_PARTIES", "500")

import streamlit as st

from app import bootstrap
from app.agent import agent
from app.layer1_data import db
from app.layer4_decisioning.decisioning import get_engine
from app.layer5_governance import audit, fairness, governance

st.set_page_config(page_title="BFSI real-time personalization",
                   page_icon="⚡", layout="wide")


@st.cache_resource(show_spinner="Bootstrapping five layers (seed → features → models → policies)…")
def _init():
    """Bootstrap once per server process; cached across reruns."""
    bootstrap.ensure()
    return get_engine()


engine = _init()


@st.cache_data
def _personas(limit: int = 25):
    rows = db.fetchall(
        "SELECT party_id, domain, journey_stage, risk_band FROM party LIMIT ?", (limit,)
    )
    return {f"{p} · {d}/{s} · {r}": p for p, d, s, r in rows}


st.title("⚡ BFSI real-time, agentic personalization")
st.caption("Five layers · agentic loop · every decision audited · sub-98ms hot path. "
           "Local stand-ins for cloud services (Postgres→Snowflake, Redis→ElastiCache, …).")

backends = db.backends()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Ledger", backends["ledger"])
c2.metric("Hot store", backends["online_store"])
c3.metric("Agent engine", "langgraph" if agent._HAS_LANGGRAPH else "hand-rolled")
c4.metric("Audit rows", audit.count())

personas = _personas()
left, right = st.columns(2, gap="large")

# --------------------------------------------------------------------------- #
# Layer 4/5 — next-best-action
# --------------------------------------------------------------------------- #
with left:
    st.subheader("Layer 4/5 · Next-best-action")
    persona_label = st.selectbox("Persona (non-PII)", list(personas))
    event_type = st.selectbox(
        "Live context event",
        ["session_start", "large_transfer_attempt", "product_page_view", "card_declined"],
    )
    if st.button("Decide", type="primary", use_container_width=True):
        party_id = personas[persona_label]
        event = {"event_type": event_type,
                 "amount": 4000 if event_type == "large_transfer_attempt" else 0}

        t0 = time.perf_counter()
        decision = engine.decide(party_id, event)
        assessment = governance.assess(engine, decision)
        latency_ms = (time.perf_counter() - t0) * 1000.0
        record = governance.build_record(decision, assessment, "web", latency_ms)
        audit.write(record)  # exactly one audit row per decision

        winner = decision["winner"]
        st.success(f"**{winner['action_id']}**  ·  expected value {winner['expected_value']}")
        m1, m2, m3 = st.columns(3)
        m1.metric("Latency", f"{latency_ms:.2f} ms", help="SLO 98ms (warm)")
        m2.metric("Within SLO", "✅" if latency_ms < 98 else "❌")
        m3.metric("Fairness", record["fairness_flag"])

        st.markdown("**Why — SHAP-style reason codes**")
        st.table([
            {"feature": r["label"], "direction": r["direction"],
             "contribution": r["contribution"], "value": r["value"]}
            for r in record["reason_codes"]
        ])
        st.markdown("**Model scores**")
        st.json({k: round(v, 4) for k, v in decision["model_scores"].items()})
        with st.expander(f"Audit row · {record['decision_id']}"):
            st.json(audit.get(record["decision_id"]))

# --------------------------------------------------------------------------- #
# Agentic layer — task loop
# --------------------------------------------------------------------------- #
with right:
    st.subheader("Agentic layer · task loop")
    agent_persona = st.selectbox("Party", list(personas), key="agent_party")
    goal = st.text_input("Goal", value="I want a pre-approved loan of 50000")
    st.caption('Try: "dispute an unauthorized charge of 15000" · "give me a financial tip"')
    if st.button("Run agent", use_container_width=True):
        party_id = personas[agent_persona]
        placeholder = st.container()
        final = None
        with placeholder:
            for ev in agent.run_stream(party_id, goal):
                if ev["type"] == "final":
                    final = ev
                else:
                    icon = "⚠️" if ev["node"] == "escalate" else "•"
                    st.markdown(f"{icon} **{ev['node']}** — {ev['detail']}")
        if final:
            if final["escalated"]:
                st.warning(f"Escalated to human review · confidence {final['confidence']} · "
                           f"engine {final['engine']}")
            else:
                st.success(f"Completed · confidence {final['confidence']} · "
                           f"engine {final['engine']}")
            st.write(final["answer"])

with st.sidebar:
    st.header("Governance")
    gov = {"drift": governance.drift_snapshot(), "fairness": fairness.snapshot(),
           "human_queue": (db.fetchone("SELECT COUNT(*) FROM human_queue") or [0])[0]}
    st.json(gov)
    st.caption("This is a structural reference demo: synthetic data, illustrative "
               "model scores. The architecture, latency and audit trail are the point.")
