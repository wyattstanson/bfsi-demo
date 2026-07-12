# BFSI real-time, agentic personalization — a structural reference demo

A small, runnable system that mirrors the **five-layer architecture** of a
production real-time personalization platform for banking, financial services
and insurance. It proves the *structure*, not feature-completeness: every box is
a local stand-in that swaps cleanly for its cloud equivalent (see the mapping
table below).

What it demonstrates:

- A `/decide` next-best-action endpoint that returns in **well under 98ms p99
  (warm)** — measured, ~2–5ms in-process — with a SHAP-style explanation, a
  fairness flag, and an **append-only audit row for every decision**.
- An **agentic loop** (perceive → reason → act → observe → escalate) running on
  the same data, using MCP-style tools, vector memory, and a hard
  **human-escalation** path on low confidence / high stakes.
- The BFSI vocabulary throughout: domains (retail, wealth, payments, nbfc,
  insurance) and journey stages (discover, originate, engage, cross-sell,
  service, retain).

## The five layers

| Layer | Folder | Does |
|------|--------|------|
| 1 · Data Foundation | `app/layer1_data` | System-of-record ledger + online hot-path store + CDC event stream |
| 2 · Feature Store | `app/layer2_features` | One feature definition, served offline (train) and online (`get_online_features`, sub-ms) with a `domain__entity__metric__window` naming convention |
| 3 · Models | `app/layer3_models` | Propensity + churn, uplift/X-learner, graph fraud score, grounded (RAG) LLM helper |
| 4 · Decisioning | `app/layer4_decisioning` | Real-time engine: online features → model scores → eligibility + do-no-harm rules (`action_catalog.yaml`) → LinUCB ranking |
| 5 · Governance | `app/layer5_governance` | SHAP-style reasons, adverse-impact fairness, drift counters, 16-field append-only `audit_log` |
| Agentic | `app/agent` | Stateful graph, MCP-style tool registry, pgvector memory, human queue |

## Run it

Zero infrastructure is required — the demo falls back to SQLite + an in-process
store and runs entirely offline.

```bash
pip install -r requirements.txt          # core deps install on Python 3.11–3.13
python -m app.bootstrap                   # seed → features → models → policies (one-time)
python -m uvicorn app.main:app --port 8000
# open http://127.0.0.1:8000
```

Prove the acceptance checks:

```bash
python -m pytest tests/ -q -s             # latency<98ms, one-audit-row, escalation, no-PII
python -m scripts.benchmark 500           # prints p50/p95/p99, asserts p99 < 98ms
```

### Optional: exercise the "full" stack

```bash
docker compose up -d                      # postgres(pgvector) + redis
# then in .env:
#   DATABASE_URL=postgresql://bfsi:bfsi@localhost:5432/bfsi
#   REDIS_URL=redis://localhost:6379/0
```

The code path is identical; only the backends change (`GET /health` reports which
are active). Set `ANTHROPIC_API_KEY` to replace the offline LLM stub with a
hosted Claude model for the agent's grounded answers.

#### Docker smoke test

`scripts/smoke_docker.py` is a one-command end-to-end check against the real
stack. It brings the compose services up (`--wait` on their healthchecks), points
the app at Postgres + Redis, then asserts:

- `GET /health` reports **postgres** as the ledger and **redis** as the hot store;
- a `/decide` call writes **exactly one** audit row and stays under the 98ms SLO;
- the JSONB audit columns (`features_snapshot`, `reason_codes`, …) round-trip
  through Postgres and the row is queryable by `decision_id`;
- an agent escalation lands a row in the Postgres `human_queue` table;
- vector memory is populated in `agent_memory`.

```bash
pip install "psycopg[binary]" redis
python -m scripts.smoke_docker            # up, test, leave services running
python -m scripts.smoke_docker --down     # up, test, then `docker compose down -v`
```

Requires a working Docker engine (Docker Desktop needs a **WSL2 or Hyper-V**
backend on Windows). If the daemon is unreachable the script exits fast with a
clear message rather than hanging.

## API

| Method | Path | Purpose |
|-------|------|---------|
| POST | `/decide` | `{party_id, event, channel}` → `{action, score, reason_codes, fairness_flag, latency_ms, decision_id, …}` |
| POST | `/agent` | `{party_id, goal}` → SSE stream of loop steps, then a final result |
| GET | `/personas` | non-PII sample parties for the UI |
| GET | `/audit/{decision_id}` | the 16-field audit row |
| GET | `/governance` | drift + fairness snapshots, audit/human-queue counts |
| GET | `/health` | active backends + counts |

## Design decisions (deliberate)

- **Two stores, by design.** Redis / in-process on the sub-98ms hot path;
  Postgres / SQLite as the ledger. No general-purpose or document store is added
  — it would be neither the ledger nor on the hot path.
- **CDC is faked with a Redis-fed stub** so it runs on one laptop; the code marks
  exactly where Kafka/MSK + Flink slot in (`# TODO: swap for Kafka/MSK + Flink`).
- **PII never reaches a model.** The ledger holds name/email/ssn; the hot path
  and every model/LLM payload carry ids + non-PII only. Enforced by
  `tools.assert_no_pii` and a dedicated test.
- **Every decision is regulated.** `governance.build_record` + `audit.write` run
  inside the measured request; no response is returned without its audit row.
- **Graceful degradation is the fallback strategy, not the design.** XGBoost →
  sklearn, EconML → sklearn T-learner, torch-geometric → networkx, LangGraph →
  hand-rolled driver, hosted LLM → offline stub. Each carries a `# PROD:` note.
  `GET /health` and the `/decide` response report which implementation is live.

## From demo to production

Production is a series of **swaps**, not a rewrite — the five-layer folders and
their contracts stay put.

| Layer / piece | Local (this demo) | Production swap |
|---|---|---|
| System of record | SQLite (`layer1_data/db.py`) | **Snowflake + Databricks** (lakehouse) |
| Online hot-path store | in-process dict / Redis | **ElastiCache (Redis) / DynamoDB** |
| Streaming / CDC | `cdc_stub.py` (Redis-fed) | **Kafka / MSK + Flink** |
| Feature store | `feature_store.py` | **Feast / Databricks Feature Store + Tecton-style serving** |
| Vector store | JSON embeddings + Python cosine | **pgvector** (ivfflat), then a managed vector DB |
| Models | local pickled artifacts | **SageMaker / Databricks Model Serving** |
| Propensity / churn | XGBoost → sklearn | XGBoost on SageMaker |
| Uplift | EconML X-learner → sklearn T-learner | EconML on SageMaker |
| Fraud | networkx PageRank → (torch-geometric) | **GraphSAGE/GAT** on a graph feature store |
| Grounded LLM | offline stub | **Bedrock / hosted Claude** |
| Bandit | in-memory LinUCB | managed bandit/RL service, arm state persisted |
| Explanations | baseline SHAP approximation | `shap` on the served model |
| Fairness / drift | in-memory counters | monitored fairness + drift service |
| Audit log | `audit_log` table | **Unity Catalog + ModelOp** lineage |
| Agent runtime | hand-rolled / LangGraph | **LangGraph on EKS + real MCP** tool server |
| Tools | mocked (`agent/tools.py`) | MCP server over core banking / bureau / sanctions / ledger |

## Acceptance checks

- `python -m app.bootstrap` then `uvicorn app.main:app` boots with no manual
  steps beyond `.env`. ✅
- `POST /decide` returns the required fields and `latency_ms` < 98 warm;
  `scripts/benchmark.py` prints p99 < 98ms. ✅
- Exactly one `audit_log` row per decision (`test_audit.py`). ✅
- `POST /agent` streams loop steps and either completes or escalates to
  `human_queue` (`test_agent_escalation.py`). ✅
- Model/LLM payloads carry ids, not PII (`test_no_pii_to_model.py`). ✅
