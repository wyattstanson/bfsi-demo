# Pitch Deck Outline — BFSI Personalization (pitch.pptx)

> Auto-extracted slide text from `pitch.pptx` (20 slides). Kept in-repo so the
> demo narrative is version-controlled alongside the app. Narration lives in
> [`demo_script.md`](demo_script.md). 3D models on slides 6/8/10 use
> `arch.glb`, `rt.glb`, `ag.glb` (`MODEL3D::` placeholders below).

## Slide 1
- BFSI PLAYBOOK  /  TREDENCE  /  2026
- Personalization in BFSI
- How we build your demo, and surpass the current standard
- A client briefing: the global evidence, the architecture, the real-time agentic stack, three interactive 3D models, and a plan to not just match the leaders but beat them on latency, autonomy and governance.
- Domains  /  Case studies  /  3D models  /  Sub-98ms  /  The demo
- Aryansh  /  AI Intern, Tredence Inc.
- PERSONALIZATION IN BFSI  /  CLIENT BRIEFING  /  TREDENCE 2026
- 1 / 20

## Slide 2
- THE STAKES
- A $200M to $1B+ P&L lever, proven across every region
- $200M-$1B+
- Annual P&L for a Tier-1 firm at maturity
- +29%
- DBS outward-payment lift from personalization
- 60% / 2-4x
- HSBC fraud alert cut and detection lift
- $3-5T
- Agentic commerce flow by 2030
- 14M / 100M+
- Monzo and Nubank personalized customers
- <98ms
- The budget we commit to and prove
- THE MESSAGE
- The economics are settled and the architecture has converged, in the US, Europe and Asia alike. The question is execution, and whether a partner can surpass the standard, not just meet it.
- PERSONALIZATION IN BFSI  /  CLIENT BRIEFING  /  TREDENCE 2026
- 2 / 20

## Slide 3
- THE SUMMARY SHEET
- Every domain we personalize, across banking, markets and insurance
- BANKING
- Retail
- Real-time NBA, grounded GenAI
- +5-15% rev/active
- Corporate
- RM co-pilot, treasury
- +10-20% wallet
- Wealth
- Advisor co-pilot, tax-aware
- +25-40% productivity
- FINANCIAL SERVICES
- Asset mgmt
- Direct indexing, per-client SMA
- 25-45 bps fee
- Payments
- Agentic commerce, sub-50ms fraud
- +10-20% volume
- Capital markets
- Research, RFQ, domain LLMs
- +10-25% wallet
- NBFC / lending
- AA underwriting, vernacular voice
- 30-50% faster
- INSURANCE
- Personal / life
- Wellness, telematics
- 3-5 pt loss ratio
- General P&C
- Geospatial, STP claims
- 3-5 pt combined
- Commercial
- Cyber pricing, MGA triage
- +50-100% throughput
- PERSONALIZATION IN BFSI  /  CLIENT BRIEFING  /  TREDENCE 2026
- 3 / 20

## Slide 4
- THE GLOBAL EVIDENCE
- The leaders we benchmark against, region by region
- UNITED STATES
- BofA Erica (2B+, sub-44ms), JPMorgan Connect, Capital One, Aladdin at Morgan Stanley, Stripe Radar, Lemonade, Progressive, State Farm, John Hancock Vitality, Mastercard Agent Pay.
- EUROPE AND THE UK
- Santander (60+ AI use cases, first live agentic payment), HSBC federated GNN (60% fewer alerts), BBVA, ING, Lloyds, Monzo (14M), Revolut AIR (13M), Klarna.
- INDIA AND ASIA
- Bajaj FINAI (800+ agents target, ~555B AUM), DBS (1,500+ models, world's best AI bank, +29% payments), HDFC PIXEL, Ant Group, WeBank, KakaoBank, Nubank (100M+).
- Audited, in-production numbers, not projections. The bar is high, and public.
- PERSONALIZATION IN BFSI  /  CLIENT BRIEFING  /  TREDENCE 2026
- 4 / 20

## Slide 5
- WHERE YOU ARE, WHERE WE TAKE YOU
- The four-stage maturity model
- 1  RULES
- Yesterday
- Hard-coded rules and a few segments. Click-through 1 to 2 percent.
- 2  BATCH ML
- Today, most
- Propensity on history via a CDP. 2 to 3x conversion. The baseline.
- 3  REAL-TIME
- Today, leaders
- Sub-100ms event-stream, bandits, uplift. One brain, every channel.
- 4  AGENTIC
- The frontier, where we take you
- Autonomous agents that perceive, reason, act and escalate. Governed per decision.
- Most Tier-1 firms sit at stage two to three. We build you to stage four, on the same five-layer structure, with governance shipped per decision.
- PERSONALIZATION IN BFSI  /  CLIENT BRIEFING  /  TREDENCE 2026
- 5 / 20

## Slide 6
- THE UNIVERSAL BLUEPRINT
- One five-layer architecture, shown in 3D
- MODEL3D::arch
- 5
- Governance
- explainability, audit log per decision
- 4
- Decisioning
- real-time engine, sub-98ms
- 3
- Models and Reasoning
- XGBoost, GNN, uplift, LLM, agents
- 2
- Feature Store
- governed online and offline
- 1
- Data Foundation
- lakehouse, CDC, streaming, state
- The differences sit inside each layer, not between architectures.
- CLICKABLE 3D MODEL
- In PowerPoint desktop, click the model and drag its centre handle to rotate, or right-click for Pan and Zoom.
- PERSONALIZATION IN BFSI  /  CLIENT BRIEFING  /  TREDENCE 2026
- 6 / 20

## Slide 7
- THE REFERENCE STACK
- Built on AWS, Snowflake and Databricks
- DATABRICKS
- Build it
- Delta Lake + Structured Streaming
- Feature Store, Mosaic AI
- Model Serving, Unity Catalog
- SNOWFLAKE
- Govern it
- Certified data marts
- Snowpipe Streaming, Snowpark
- Row and column governance
- AWS
- Serve it
- MSK / Kinesis streaming
- DynamoDB, ElastiCache (Redis)
- SageMaker, Bedrock, EKS
- Databricks builds it, Snowflake governs it, AWS serves it in real time. Execution beats vendor selection.
- PERSONALIZATION IN BFSI  /  CLIENT BRIEFING  /  TREDENCE 2026
- 7 / 20

## Slide 8
- REAL-TIME, SUB-98MS
- The real-time pipeline, shown in 3D
- MODEL3D::rt
- THE LATENCY BUDGET (p99)
- Feature fetch, online store
- ~5 ms
- Serialization, protobuf
- ~4 ms
- Model inference, GBM
- ~12 ms
- Rules and ranking
- ~8 ms
- Network and overhead
- ~6 ms
- ROUND TRIP
- about 35ms p99, we commit to under 98ms
- CLICKABLE 3D MODEL
- In PowerPoint desktop, click the model and drag its centre handle to rotate, or right-click for Pan and Zoom.
- PERSONALIZATION IN BFSI  /  CLIENT BRIEFING  /  TREDENCE 2026
- 8 / 20

## Slide 9
- WHY THE STACK HOLDS, AT SCALE
- Optimal for real-time and for tens of millions of customers
- In-memory online store
- DynamoDB, ElastiCache
- Single-digit-ms reads at any scale; no query in the hot path.
- Event-time streaming
- Databricks + Flink
- Exactly-once state, so a payment is never double-counted.
- Compute once, serve millions
- Feature Store
- A feature is engineered once and read by every model and channel.
- Right-sized serving
- SageMaker, Triton
- Boosted trees in 5 to 30ms on CPU; warm pools, no cold starts.
- Partitioned throughput
- Kafka / MSK
- Millions of events per second; consumers scale with load.
- Cost stays linear
- open formats, spot
- Separate storage and compute keep unit cost flat as volume grows.
- PERSONALIZATION IN BFSI  /  CLIENT BRIEFING  /  TREDENCE 2026
- 9 / 20

## Slide 10
- THE FRONTIER
- The agentic loop, shown in 3D
- MODEL3D::ag
- 1
- Perceive, Reason, Act, Observe
- the four loop steps on the ring
- 2
- Tools via MCP
- CRM, core, bureau, ledger
- 3
- Memory
- the vector database, left node
- 4
- Human escalation
- policy routes to a person, top
- 5
- Governed and logged
- every action audited
- Bajaj FINAI closes loans this way, escalating to a human whenever policy demands.
- CLICKABLE 3D MODEL
- In PowerPoint desktop, click the model and drag its centre handle to rotate, or right-click for Pan and Zoom.
- PERSONALIZATION IN BFSI  /  CLIENT BRIEFING  /  TREDENCE 2026
- 10 / 20

## Slide 11
- WHY THE STACK FOR AGENTIC DATA
- Reliable, auditable autonomy by design
- Stateful orchestration
- LangGraph on EKS
- A graph of steps, inspectable and resumable, which regulators require.
- Memory-first
- vector database
- Embeddings and retrieval give the agent memory across sessions.
- Governed tools
- Model Context Protocol
- One control point for the 10 to 50 tools an agent calls.
- Guardrails
- policy + PII isolation
- Constrain tools; keep account data out of the model payload.
- Observability
- tracing + evaluation
- See, explain and replay non-deterministic runs; prove compliance.
- Human in the loop
- escalation path
- Low confidence or high stakes routes to a person with full context.
- PERSONALIZATION IN BFSI  /  CLIENT BRIEFING  /  TREDENCE 2026
- 11 / 20

## Slide 12
- THE MODEL TOOLKIT
- Eight patterns cover almost every use case
- 1
- Tabular ML
- XGBoost, LightGBM
- Credit, fraud, churn
- 2
- Causal uplift
- EconML X-Learner
- 20-40% ROI over propensity
- 3
- Recommendation
- Two-tower DNN
- NBA, research, product rec
- 4
- Graph neural nets
- GraphSAGE, HinSAGE
- Fraud, AML; HSBC 60% cut
- 5
- Grounded LLMs
- LangChain + vector
- Servicing, co-pilot
- 6
- Agentic AI
- LangGraph, CrewAI
- Bajaj, Aladdin, Agent Pay
- 7
- Reinforcement
- Contextual bandits
- NBA, pricing, rebalancing
- 8
- Sequence models
- LSTM, TFT
- Soft-churn, CLV
- PERSONALIZATION IN BFSI  /  CLIENT BRIEFING  /  TREDENCE 2026
- 12 / 20

## Slide 13
- THE DIFFERENTIATOR
- Governance: thirteen regimes, one audit log
- EU AI Act
- High-risk credit and insurance pricing. Conformity, oversight, logging.
- Fair lending and suitability
- ECOA, Reg B, MiFID II, Reg BI, FINRA 2111. SHAP-driven adverse-action notices.
- Data rights and consent
- GDPR Art 22, DPDPA, CFPB 1033, India Account Aggregator, PSD2 and PSD3.
- Model risk and insurance AI
- SR 11-7, OCC 2011-12, NAIC AI Bulletin, RBI Digital Lending.
- THE ENGINEERING ANSWER
- One well-designed audit log per decision answers all thirteen at once. We ship it with every decision, so the system is conformity-ready on day one.
- PERSONALIZATION IN BFSI  /  CLIENT BRIEFING  /  TREDENCE 2026
- 13 / 20

## Slide 14
- PROOF WE DRAW FROM
- The marquee references, and the lesson from each
- HSBC federated GNN
- 60% / 2-4x
- governed, federated fraud; the model travels, the data stays
- Bajaj FINAI
- 800+ agents
- agentic lending at national scale; our Stage 4 reference
- BlackRock Aladdin
- $23T AUM
- grounded GenAI with a human always in the loop
- DBS
- 1,500+ models
- one brain, 150M nudges a month, +29% payments
- Nubank
- 100M+ / 1/8 cost
- clean data foundation beats a branch network
- Lemonade
- 3-sec claims
- straight-through processing and grounded conversation
- PERSONALIZATION IN BFSI  /  CLIENT BRIEFING  /  TREDENCE 2026
- 14 / 20

## Slide 15
- NOT JUST MEETING THE STANDARD
- Five ways we surpass it
- 1
- Sub-98ms, and prove it
- We commit to a benchmarked sub-98ms p99, tighter than the sub-100ms the leaders quote.
- 2
- Agentic by default
- The agentic loop is first-class from day one, with the same audit log as the real-time path.
- 3
- Governance as a product
- The audit log, SHAP, fairness flag and consent receipt ship with every decision.
- 4
- Causal by default
- We target uplift, the persuadable customer, capturing 20 to 40 percent more return.
- 5
- A structure built to expand
- Every layer present, every control enforced, every box swaps for its cloud service.
- PERSONALIZATION IN BFSI  /  CLIENT BRIEFING  /  TREDENCE 2026
- 15 / 20

## Slide 16
- WHAT WE BUILD FIRST
- The demo: lean, but structurally the real thing
- 5
- Data Foundation
- Postgres + pgvector + Redis, synthetic BFSI personas, a CDC stub
- 4
- Feature Store
- Postgres views and Redis online store, freshness SLAs
- 3
- Models
- XGBoost + EconML uplift + a small GNN + a LangGraph agent
- 2
- Decisioning
- FastAPI rules engine + bandit, a sub-100ms decision endpoint
- 1
- Governance
- SHAP per decision + fairness flag + an audit-log row
- WHAT IT PROVES
- All five layers, end to end
- A sub-98ms decision, benchmarked
- Uplift beats propensity
- One live agent with memory
- An audit row per decision
- PERSONALIZATION IN BFSI  /  CLIENT BRIEFING  /  TREDENCE 2026
- 16 / 20

## Slide 17
- FROM DEMO TO PRODUCTION
- Swap each box for its cloud service. No re-architecture.
- DEMO (build now)
- PRODUCTION (expand into)
- Data Foundation
- Postgres + pgvector + Redis
- Snowflake + Databricks + DynamoDB / ElastiCache
- Feature Store
- Postgres views, in-process
- Databricks Feature Store or Tecton
- Models
- XGBoost + LangGraph local
- SageMaker / Model Serving + LangGraph on EKS + MCP
- Decisioning
- FastAPI rules + bandit
- Pega CDH or FastAPI on EKS + Kafka / Flink
- Governance
- Postgres audit + SHAP
- Unity Catalog + ModelOp + audit log per decision
- Because both share the five-layer shape, expansion is a series of swaps, not a rebuild.
- PERSONALIZATION IN BFSI  /  CLIENT BRIEFING  /  TREDENCE 2026
- 17 / 20

## Slide 18
- THE PLAN
- A twelve-month roadmap, value early
- Weeks 1-6
- Data foundation, models, and the sub-98ms decision endpoint, benchmarked
- Weeks 7-10
- Grounded co-pilot, the agentic workflow with MCP tools, and graph fraud
- Weeks 11-12
- Governance layer and the persona-switcher frontend; record the demo
- Months 4-6
- Swap local stores for Snowflake, Databricks, DynamoDB; streaming to Kafka and Flink
- Months 7-12
- Scale the first production sub-vertical; pass a conformity assessment; measure causal lift
- PERSONALIZATION IN BFSI  /  CLIENT BRIEFING  /  TREDENCE 2026
- 18 / 20

## Slide 19
- THE ECONOMICS
- Where the $200M to $1B+ comes from
- RETAIL BANKING
- +5-15% rev/active
- $200-800M for a 20M-active Tier-1
- WEALTH
- +25-40% productivity
- $1-4B on a $1T franchise
- PAYMENTS
- +10-20% volume
- billions in interchange and avoided fraud
- INSURANCE
- 3-5 pt loss ratio
- $150M on a $5B premium book, per 3 points
- NBFC / LENDING
- 30-50% faster
- thousands of crores of well-underwritten book
- THE MULTIPLIER
- +20-40% causal
- every campaign, plus fines avoided by governance
- Defensible from the bottom up, sub-vertical by sub-vertical, and measured causally against a holdout, which is exactly the discipline a chief financial officer will demand.
- PERSONALIZATION IN BFSI  /  CLIENT BRIEFING  /  TREDENCE 2026
- 19 / 20

## Slide 20
- THE PROMISE
- 1
- We match the leaders on the fundamentals
- The same five-layer structure on AWS, Snowflake and Databricks, governed per decision.
- 2
- We surpass them where it counts
- A sub-98ms budget, agentic and causal by default, governance shipped with every decision.
- 3
- We prove it small, then scale by swapping
- A lean demo that is structurally the real thing, expanding to production without a rewrite.
- Aryansh  /  Tredence Inc.  /  Personalization in BFSI  /  Let us build it
