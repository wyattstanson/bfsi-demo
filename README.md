# Aria, a BFSI Personalization Platform

[![CI](https://github.com/wyattstanson/bfsi-demo/actions/workflows/ci.yml/badge.svg)](https://github.com/wyattstanson/bfsi-demo/actions/workflows/ci.yml)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/wyattstanson/bfsi-demo)

Aria decides the next-best-action for every customer interaction, explains it in
plain language, keeps a regulator-ready audit trail, and hands the hard calls to a
human. It is a real-time, explainable, agentic personalization platform for banking,
financial services and insurance, patterned on the products that set the bar: BofA
Erica (sub-44ms, 2B interactions), BlackRock Aladdin (23T dollars AUM), Lemonade
(3-second claims) and Bajaj FINAI (800+ autonomous agents).

The same decision engine is shown through five points of view, so a customer, an
advisor, an executive, a regulator and an engineer each see what matters to them.

## Five points of view

Open the platform and pick a lens. The first four are customer and business facing.
The fifth is restricted.

| Mode | Who it is for | What it shows |
|------|---------------|---------------|
| Concierge | The person on the app | A warm, personal moment. Plain language, no scores. An assistant, Ava, that acts end to end and brings in a human when needed. |
| Co-pilot | The relationship manager | A ready-to-use brief, the recommended action, drivers, talking points and a suitability note, in the style of Aladdin Auto-Commentary. |
| Control Tower | The C-suite | The book of decisions. Value captured, latency against budget, fairness, and a live decision stream, by action and by region. |
| Assurance | The supervisor | Every consequential decision with SHAP reason codes, an adverse-impact fairness signal, and a replayable 16-field audit record. |
| Engine Room | The AI engineer | Under the hood. The five-layer pipeline, warm latency percentiles, the model registry, the live CDC event stream and the raw agentic trace. Passcode protected. |

A light and dark theme are both available, toggled from the header.

The Developer mode passcode is `Aryansh@Tredence` (override with the `DEV_PASSCODE`
environment variable).

## Architecture

```mermaid
flowchart LR
  T["Customer touchpoint"] --> APP["Aria app<br/>landing, five modes, Ava"]
  APP --> DEC["L4 Decisioning<br/>rules + LinUCB bandit"]
  DEC --> FS["L2 Feature store<br/>online read, sub-ms"]
  DEC --> MOD["L3 Models<br/>propensity, uplift, fraud, LLM"]
  DEC --> GOV["L5 Governance<br/>SHAP, fairness, 16-field audit"]
  FS --> HOT[("Hot store<br/>Redis / Upstash")]
  GOV --> LED[("Ledger<br/>Postgres / Neon + pgvector")]
  APP --> AG["Agentic loop<br/>perceive, reason, act, observe"]
  AG --> HQ[("Human queue")]
  CDC["Event stream<br/>Kafka + Flink (prod), stub (demo)"] --> HOT
```

| Layer | Folder | Responsibility |
|------|--------|----------------|
| 1 Data Foundation | `app/layer1_data` | Ledger, online hot store, live CDC event stream |
| 2 Feature Store | `app/layer2_features` | Offline and online serving, sub-ms, `domain__entity__metric__window` keys |
| 3 Models | `app/layer3_models` | Propensity, churn, uplift, graph fraud score, grounded LLM |
| 4 Decisioning | `app/layer4_decisioning` | Online features, model scores, eligibility and do-no-harm rules, LinUCB ranking |
| 5 Governance | `app/layer5_governance` | SHAP reason codes, adverse-impact fairness, drift, 16-field audit log |
| Agent | `app/agent` | Stateful loop, MCP-style tools, vector memory, human escalation |

## Run it locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --port 8000     # the Aria platform, open http://127.0.0.1:8000
```

The first request runs a one-time bootstrap (seed, features, models, policies). With
no services configured it uses SQLite and an in-process store. Verify:

```bash
python -m pytest tests/ -q            # latency, one-audit-row, escalation, no-PII
python -m scripts.benchmark 800       # warm p50/p95/p99, asserts p99 under 98ms
```

A lightweight Streamlit build of the same engine is also included
(`streamlit run streamlit_app.py`).

## Deploy the platform

The Aria website is served by FastAPI, so deploy it as a web service. A free
[Render](https://render.com) blueprint is included:

1. Push this repo to GitHub.
2. On Render, New, Blueprint, and point it at the repo. `render.yaml` provisions a
   free Python web service running `uvicorn app.main:app`.
3. Optionally set `DATABASE_URL`, `REDIS_URL` and `ANTHROPIC_API_KEY` in the service
   settings to attach a persistent database and live Claude grounding.

## Data at scale, local to global

The dataset spans the dossier's ten BFSI sub-verticals (retail, corporate, wealth,
asset management, payments, capital markets, NBFC, personal, general and commercial
insurance) across six regions and currencies. The demo seeds a few thousand synthetic
parties for a snappy start. To move from a small local set to a global one:

```bash
python -m scripts.seed_bulk 1000000   # loads a million parties (Postgres COPY fast path)
```

The app never loads the whole population into memory. It warms features on demand per
requested party, materializes and trains on a representative sample (`MATERIALIZE_CAP`,
default 25000), and serves any of the millions from the ledger. Point `DATABASE_URL`
at a hosted Postgres and `REDIS_URL` at a hosted Redis and the same code runs at
global scale. A live CDC event stream drives the real-time and agentic feeds.

## Persistent cloud database

Set two environment variables and the backends switch with no code change:

```toml
DATABASE_URL = "postgresql://USER:PWD@HOST-pooler.REGION.neon.tech/DB?sslmode=require"
REDIS_URL    = "rediss://default:PWD@HOST.upstash.io:6379"
```

Neon and Supabase give free Postgres with pgvector; Upstash gives free Redis. CI runs
the entire suite against a real Postgres (pgvector) plus Redis on every push, so the
database path is verified, not just SQLite.

## From demo to production

| Piece | Local | Production |
|---|---|---|
| Ledger | SQLite | Snowflake and Databricks, or Neon and Aurora Postgres |
| Hot store | in-process dict | ElastiCache, DynamoDB, or Upstash |
| Streaming | `cdc_stub.py` | Kafka and MSK plus Flink |
| Feature store | `feature_store.py` | Feast, Databricks, Tecton |
| Vector memory | JSON and Python cosine | pgvector, then a managed vector DB |
| Models | pickled artifacts | SageMaker or Databricks Model Serving |
| Fraud | networkx PageRank | GraphSAGE and GAT on a graph feature store |
| Grounded LLM | offline stub | Bedrock or a hosted Claude endpoint |
| Explanations | linear and baseline SHAP | the `shap` library on the served model |
| Audit log | `audit_log` table | Unity Catalog and ModelOp lineage |
| Agent runtime | hand-rolled or LangGraph | LangGraph on EKS with a real MCP server |

## Design decisions

* Every decision is regulated. Governance runs inside the measured request and no
  response is returned without its audit row.
* PII never reaches a model. Names, emails and identifiers stay in the ledger. The
  hot path and every model and LLM payload carry ids and non-PII features only. A test
  enforces it.
* Latency first. The LinUCB inverse is cached and refreshed only on learning, so a
  decision does zero matrix inversions, and reason codes are exact linear attributions
  for logistic models. Warm p99 is in the single-digit milliseconds.
* Graceful degradation. XGBoost to sklearn, EconML to a sklearn T-learner,
  torch-geometric to networkx, LangGraph to a hand-rolled driver, hosted LLM to an
  offline stub, Postgres to SQLite, Redis to an in-process store. `GET /health`
  reports which implementation is live.
