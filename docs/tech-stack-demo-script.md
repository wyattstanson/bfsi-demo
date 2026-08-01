# Tech-Stack Demo Script, Why We Built It This Way

**Audience:** client architects, a VP, an AI engineer in the room. **Length:** 8 to 10 minutes. **Where:** the Engine Room view of Aria, plus the Industry Reference panel inside it. **Tone:** calm, evidence-first, engineer to engineer. Pause after every number.

Delivery rule: every choice in this stack is a latency decision, a governance decision, or a cost decision, and usually two of the three. Say which one out loud each time. That is what makes it sound designed, not assembled.

---

## [0:00] Opening, the one sentence

> What you are looking at is a real-time personalization engine that returns a governed decision in under ninety-eight milliseconds, and then proves it. Every piece of this stack was chosen for one of three reasons: speed, governance, or cost. Let me walk you through the decisions, not just the diagram.

---

## [0:30] The five layers, and why they exist at all

*Point at the pipeline strip: L1 Data, L2 Features, L3 Models, L4 Decisioning, L5 Governance.*

> The industry has converged on the same five layers, from Capital One to DBS to Bajaj. That is not fashion, it is physics. You need clean data, you need features computed once and served fast, you need models, you need something that turns scores into a decision under a time budget, and you need governance on every single decision. Firms do not differ on the layers. They differ on the quality of what sits inside each one. So let me show you what we put inside each, and why.

---

## [1:15] Layer 1 and 2, why a key-value feature store, not a database join

*Open the Industry Reference panel, point at the blueprint layers.*

> The single most important latency decision is here. In the hot path we never do a relational join. We read features from a key-value store, Redis in the demo, Aerospike or DynamoDB in production, because a KV lookup is a predictable single-digit millisecond read and a join is not. PayPal makes exactly this choice, Aerospike for real-time feature retrieval, and it is why about seventy-five percent of their risk decisions land under fifty milliseconds. A feature store also kills training-serving skew: the same feature definition feeds offline training and online scoring, so the number the model trained on is the number it sees in production. That is a correctness decision as much as a speed one.

**Why not just query Postgres in-path?** Because a join under load has a long tail, and personalization lives and dies on the p99, not the average. We move the work off the hot path instead.

---

## [2:30] Layer 3, why gradient-boosted trees beat deep learning in the path

*Point at Model Serving in the blueprint, latency chip 20 to 40 ms.*

> For real-time transaction scoring we serve XGBoost and LightGBM, tree models, not deep nets. This surprises people. The reason is latency and explainability together. Trees score in microseconds on tabular data, they are cheaper to run, and their reason codes are exact, which the regulator wants. We reserve deep learning for the few high-value card-not-present cases where the accuracy is worth the milliseconds. Visa runs exactly this split, gradient-boosted trees plus deep learning only where it pays. You do not need a hundred models, you need about eight patterns done well: propensity, uplift, recommendation, fraud graphs, grounded language models, and agents.

---

## [3:30] Layer 4, why a cached bandit, not a fresh optimization every call

> Decisioning ranks every eligible action by expected value under the rules. We use a LinUCB contextual bandit, and the trick is that we cache the matrix inverse and refresh it only when the model learns, so a live decision does zero matrix inversions. That is a deliberate move to keep the hot path arithmetic-free. It is also honest exploration: the bandit keeps probing alternatives so the system never stops learning, which is how you avoid getting stuck serving yesterday's best answer.

---

## [4:15] Layer 5, why governance runs inside the decision, not after it

*Point at the Governance panel and the live audit tail.*

> This is our real differentiator, and it is a compliance decision. Governance is not a nightly batch job. It runs inside the measured request, and no response is returned without its audit row: the reason codes, the fairness check across protected groups, and the data behind the decision. Explainability is SHAP, or exact linear attributions for the logistic models, cached so it costs nothing at serve time. That is what lets a regulator ask about any one decision and get an answer, and it is what satisfies model-risk rules and the EU AI Act at the same time. Under the Act this is Annex III, high-risk: credit scoring and insurance pricing. Transparency obligations are already live as of August 2026, the high-risk deadline is deferred to December 2027, so building governance in now is not early, it is on time.

**The headroom line:** we hold the whole decision under ninety-eight milliseconds *including* the fairness and explainability work. The reason we have room for governance is that we spent the earlier budget carefully.

---

## [5:15] Why the audit write does not cost us latency

*Trigger the 120-request burst, point at the p99.*

> One more latency decision worth calling out. The ledger write is off the hot path. It is write-behind, batched every two hundred and fifty milliseconds, so a decision does zero blocking I/O. That is why throughput is CPU-bound and scales linearly: per-core rate, times cores, times autoscaled replicas on EKS, gets you past a million decisions a second without a million customers ever touching memory at once. Statelessness is the whole reason this scales by adding boxes.

---

## [6:00] The cloud layer, why AWS and Databricks and Snowflake, all three

*Point at the Production Topology and the cloud cards.*

> People ask why not pick one. Because they do different jobs, and the mature shops run them side by side.

- **AWS is the substrate.** It is the default for cloud-native banks, Capital One is the reference case, the first major bank to fully exit on-prem. It is also the host under Snowflake and Databricks even when a bank thinks it chose one of those. Compute on EKS, storage on S3 under open table formats.
- **Databricks is the ML and streaming engine.** It is the better fit for real-time fraud inference and model training. Delta Lake gives you ACID on object storage, Unity Catalog gives you lineage, which is your AI-Act audit trail, and MLflow is the model registry. Capital One's fraud work and Mastercard's Decision Intelligence both lean here.
- **Snowflake is the governed reporting layer.** High-concurrency SQL so risk, compliance, and finance all query the same governed tables at once. Virtual Private Snowflake is the single-tenant, regulated-industry variant Capital One uses.

> So the pattern is Snowflake for governed reporting, Databricks for the engineering engine, with Unity Catalog bridging governance across both. Azure enters when the client already runs Microsoft-heavy IT, which is exactly why Fiserv partners there for Copilot and AI Foundry.

---

## [7:15] The reference matrix, why the leaders diverge

*Scroll the Industry Reference matrix.*

> This is not us guessing. It is what the leaders have actually disclosed, and it teaches one lesson: the architecture is shared, the choices inside it are risk decisions.

- **Bank of America's Erica is deliberately not an LLM.** Proprietary NLP, control-and-compliance first, over two billion interactions in tens of milliseconds. That is a governance decision, not a capability gap.
- **JPMorgan, Goldman, Bajaj run model-agnostic routers,** swapping models per task and risk profile, so no single vendor owns them.
- **Lemonade pays simple claims in about three seconds** on a machine-learning core with a rules engine, the benchmark for instant experience.

> Where the internals are not public, we mark them "not public," not absent. Being honest about the gaps is what makes the rest credible.

---

## [8:15] Demo to production, why nothing gets rewritten

> Here is the promise that makes this safe to buy. The demo becomes production by swapping boxes, not by rewriting. Postgres becomes Snowflake and Databricks. Redis becomes the cloud online store. The interfaces are identical, the five layers are identical, the latency contract is identical. We prove the shape on a laptop, then scale it by swapping components behind stable interfaces. No re-architecture, no leap of faith.

---

## [8:45] Close

> So every choice here answers to speed, governance, or cost. Key-value features for speed. Trees in the path for speed and explainability. Governance inside the request for compliance. Write-behind audit for scale. AWS, Databricks, and Snowflake each doing the one job they are best at. It is not a pile of tools, it is a set of decisions, and every one of them is defensible in front of your risk committee. That is what we would build with you. Thank you.

---

## Quick answers if the room pushes back

- **"Why not deep learning everywhere?"** Latency and explainability. Trees score in microseconds with exact reason codes; we use deep nets only where the accuracy pays for the milliseconds.
- **"Why not one cloud vendor?"** They are not competing here. Databricks is the ML engine, Snowflake is the governed SQL layer, AWS is the substrate under both.
- **"Is sub-ninety-eight-milliseconds real with governance on?"** Yes, because governance is cached and the audit write is off the hot path. The burst test shows the p99 live.
- **"What about the EU AI Act?"** This is Annex III high-risk. Transparency is live now, the high-risk deadline is December 2027. Governance is built in, not bolted on, so we are ahead of it.
- **"What is not public?"** VisaNet's core-switch internals, PayPal's current cloud mix, JPMorgan's exact vector-DB and feature-store vendors, and anyone's exact p99. We flag those rather than guess.
