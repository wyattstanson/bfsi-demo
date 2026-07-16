# BFSI real-time, agentic personalization

[![CI](https://github.com/wyattstanson/bfsi-demo/actions/workflows/ci.yml/badge.svg)](https://github.com/wyattstanson/bfsi-demo/actions/workflows/ci.yml)
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=wyattstanson/bfsi-demo&branch=main&mainModule=streamlit_app.py)

A runnable, five-layer reference system for real-time, agentic personalization in
banking, financial services and insurance. It makes a personalized next-best-action
in single-digit milliseconds, explains and audits every decision, and runs an agent
that completes low-stakes tasks on its own and escalates high-stakes ones to a human.

Every component is a local stand-in that maps one to one onto a managed cloud
service, so the path to production is a series of swaps, not a rewrite.

**Live demo:** click the Streamlit badge above, or go to
[share.streamlit.io](https://share.streamlit.io), pick repo `wyattstanson/bfsi-demo`,
branch `main`, main file `streamlit_app.py`. Locally: `streamlit run streamlit_app.py`.

## What it does

* A `/decide` endpoint that returns a next-best-action in **well under the 98ms p99
  budget** (measured warm p99 around 6ms in process) with SHAP-style reason codes, a
  fairness flag, and an append-only audit row for every decision.
* An agentic loop (perceive, reason, act, observe, escalate) on the same data, using
  MCP-style tools, vector memory, and a hard human-escalation path.
* The BFSI vocabulary throughout: domains (retail, wealth, payments, nbfc, insurance)
  and journey stages (discover, originate, engage, cross-sell, service, retain).

## Architecture

```mermaid
flowchart LR
  T["Customer touchpoint"] --> APP["App layer<br/>Streamlit UI, FastAPI /decide, /agent"]
  APP --> DEC["L4 Decisioning<br/>rules + LinUCB bandit"]
  DEC --> FS["L2 Feature store<br/>online read, sub-ms"]
  DEC --> MOD["L3 Models<br/>propensity, uplift, fraud, LLM"]
  DEC --> GOV["L5 Governance<br/>reasons, fairness, audit"]
  FS --> HOT[("Hot store<br/>Redis / Upstash")]
  GOV --> LED[("Ledger<br/>Postgres / Neon + pgvector")]
  APP --> AG["Agent loop<br/>perceive, reason, act, observe"]
  AG --> HQ[("Human queue")]
  CDC["Events<br/>Kafka + Flink (prod), stub (demo)"] --> HOT
```

Two stores by design: Redis on the sub-98ms hot path, Postgres as the ledger. No
third store is added, because it would be neither the ledger nor on the hot path.

| Layer | Folder | Responsibility |
|------|--------|----------------|
| 1 Data Foundation | `app/layer1_data` | Ledger, online hot store, CDC event stream |
| 2 Feature Store | `app/layer2_features` | One definition served offline and online, sub-ms, `domain__entity__metric__window` keys |
| 3 Models | `app/layer3_models` | Propensity, churn, uplift, graph fraud score, grounded LLM |
| 4 Decisioning | `app/layer4_decisioning` | Online features, model scores, eligibility and do-no-harm rules, LinUCB ranking |
| 5 Governance | `app/layer5_governance` | Reason codes, adverse-impact fairness, drift, 16-field audit log |
| Agent | `app/agent` | Stateful loop, MCP-style tools, vector memory, human queue |

## Run it locally (zero infrastructure)

The app falls back to SQLite and an in-process store, so it runs with no services.

```bash
pip install -r requirements.txt
python -m app.bootstrap                     # seed, features, models, policies (one-time)
streamlit run streamlit_app.py              # the UI, or:
python -m uvicorn app.main:app --port 8000  # the API + a second UI at /
```

Verify:

```bash
python -m pytest tests/ -q -s               # latency, one-audit-row, escalation, no-PII
python -m scripts.benchmark 800             # prints p50/p95/p99, asserts p99 < 98ms
```

## Persistent cloud database (recommended for a shared demo)

Streamlit Cloud has an ephemeral filesystem, so the SQLite fallback resets on
redeploy. Attaching a free hosted database makes the data persist, with no code
change. The app reads two environment variables and switches backends when they are
present.

1. **Ledger:** create a free Postgres on [Neon](https://neon.tech) or
   [Supabase](https://supabase.com). Both include pgvector. Copy the pooled
   connection string.
2. **Hot store:** create a free Redis on [Upstash](https://upstash.com). Copy the
   `rediss://` URL.
3. In Streamlit Cloud, open app settings, then Secrets, and paste (see
   `.streamlit/secrets.toml.example`):

   ```toml
   DATABASE_URL = "postgresql://USER:PWD@HOST-pooler.REGION.neon.tech/DB?sslmode=require"
   REDIS_URL    = "rediss://default:PWD@HOST.upstash.io:6379"
   ```

`GET /health` reports which backends are live. This is not a paper claim: CI runs
the entire test suite against a real Postgres (pgvector) plus Redis on every push,
so the database path is verified, not just the SQLite one.

Efficiency choices: use Neon's pooled endpoint (server-side pooling that fits
serverless connection limits), both Neon and Upstash scale to zero when idle, and
the hot path only ever touches Redis while the ledger stays off the hot path.

## From demo to production

Production is a series of swaps. The five-layer folders and their contracts stay put.

| Piece | Local (this demo) | Production swap |
|---|---|---|
| Ledger | SQLite | Snowflake + Databricks, or Neon/Aurora Postgres |
| Hot store | in-process dict | ElastiCache (Redis), DynamoDB, or Upstash |
| Streaming / CDC | `cdc_stub.py` | Kafka / MSK + Flink |
| Feature store | `feature_store.py` | Feast, Databricks Feature Store, Tecton |
| Vector memory | JSON + Python cosine | pgvector (ivfflat), then a managed vector DB |
| Models | pickled artifacts | SageMaker or Databricks Model Serving |
| Fraud | networkx PageRank | GraphSAGE / GAT on a graph feature store |
| Grounded LLM | offline stub | Bedrock or a hosted Claude endpoint |
| Bandit | in-memory LinUCB | managed bandit / RL service, state persisted |
| Explanations | linear + baseline SHAP | `shap` on the served model |
| Audit log | `audit_log` table | Unity Catalog + ModelOp lineage |
| Agent runtime | hand-rolled / LangGraph | LangGraph on EKS + a real MCP server |

## API

| Method | Path | Purpose |
|-------|------|---------|
| POST | `/decide` | `{party_id, event, channel}` returns action, score, reason_codes, fairness_flag, latency_ms, decision_id |
| POST | `/agent` | `{party_id, goal}` streams loop steps, then a final result |
| GET | `/personas` | non-PII sample customers for the UI |
| GET | `/audit/{decision_id}` | the 16-field audit row |
| GET | `/governance` | drift and fairness snapshots, audit and human-queue counts |
| GET | `/health` | active backends and counts |

## Design decisions

* Every decision is regulated. Governance runs inside the measured request and no
  response is returned without its audit row.
* PII never reaches a model. The ledger holds name, email and ssn; the hot path and
  every model or LLM payload carry ids and non-PII features only. A test enforces it.
* Latency first. The hot path does zero matrix inversions per decision (the LinUCB
  inverse is cached and refreshed only on learning) and reason codes are exact linear
  attributions for logistic models, with baseline perturbation kept for tree models.
* Graceful degradation is the fallback, not the design. XGBoost to sklearn, EconML to
  a sklearn T-learner, torch-geometric to networkx, LangGraph to a hand-rolled driver,
  hosted LLM to an offline stub, Postgres to SQLite, Redis to an in-process store.
  `GET /health` reports which implementation is live.

## Acceptance checks

* `python -m app.bootstrap` then `uvicorn app.main:app` boots with no manual steps.
* `POST /decide` returns the required fields and warm `latency_ms` under 98;
  `scripts/benchmark.py` prints p99 under 98ms.
* Exactly one `audit_log` row per decision (`test_audit.py`).
* `POST /agent` streams steps and either completes or escalates to `human_queue`
  (`test_agent_escalation.py`).
* Model and LLM payloads carry ids, not PII (`test_no_pii_to_model.py`).
* CI runs the whole suite on SQLite (Python 3.11 and 3.12) and on Postgres + Redis.
