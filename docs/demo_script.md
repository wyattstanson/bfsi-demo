# Demo Recording Script - BFSI Personalization Pitch

**Deck:** pitch.pptx (20 slides)  ·  **Target length:** 5 to 7 minutes  ·  **Audience:** client / VP

---

## Before you hit record (pre-flight)

1. Open `pitch.pptx` in the **PowerPoint desktop app**. Confirm the three 3D models are on slides 6, 8 and 10 (arch, rt, ag). If a slide shows a placeholder box, Insert -> 3D Models -> This Device -> pick the matching `.glb` from your Downloads folder.
2. **Practice the rotation once.** In Slide Show mode a 3D model is interactive: click it and drag slowly to orbit. Do a dry run on each of the three model slides so the motion is smooth and the labels stay readable.
3. Recorder: use OBS, Zoom, or PowerPoint's own **Record** tab. Set **1080p**, hide the cursor except when you rotate a model.
4. Start in **Slide Show -> From Beginning**. Quiet room, mic check, water nearby.
5. Pace: speak at a calm, deliberate pace. The timings below assume roughly 140 words a minute with short pauses. Let the model rotations breathe.

Delivery rule: warm, confident, evidence-first. Pause after each number. Never rush the three model slides, they are the moments that land.

---

## The script (slide by slide)

**[0:00] Slide 1 - The title**
> Good morning. What you are looking at is our personalization playbook for BFSI. In the next six minutes I will show you the size of the prize, the architecture that captures it, and exactly what we will build for you first. Let us start with why this matters.

**[0:15] Slide 2 - The stakes**
> For a Tier-1 institution, personalization done properly is a two-hundred-million to one-billion-dollar swing in annual profit. That is not a marketing figure. It is the sum of measured effects: more revenue per customer in retail, higher advisor productivity in wealth, lower fraud in payments, better loss ratios in insurance. And it has been proven in every region, not just Silicon Valley.

**[0:40] Slide 3 - The summary sheet**
> This is the whole board on one page. Every domain we personalize, across banking, markets and insurance. Retail, wealth, payments, cards, lending, and every major insurance line. The key point is that one engine serves all of them. You do not buy a tool per domain. You build one brain.

**[1:05] Slide 4 - The global evidence**
> These are the leaders we benchmark against, region by region. The United States, Europe and the UK, India, and East Asia. Capital One and JPMorgan, DBS in Singapore, Bajaj and HDFC in India. The lesson from every one of them is the same: the winners treat personalization as infrastructure, not a campaign.

**[1:25] Slide 5 - The maturity model**
> Here is the honest map of where most institutions sit today, and where we take you. Four stages: batch segments, real-time triggers, a unified decisioning brain, and autonomous agents. Most banks are at stage one or two. Our job is to move you to three and four without a rebuild.

**[1:45] Slide 6 - The universal blueprint (ROTATE THE MODEL)**
> This is the architecture that makes it possible, and it is the same five layers in every serious firm on earth.
>
> *[Click the model, drag slowly to rotate.]*
>
> At the bottom, the data foundation. Above it, the feature store. Then the models. Then real-time decisioning. And across the top, governance on every single decision.
>
> *[Let it keep turning as you finish.]*
>
> The difference between firms is not the layers. It is the quality of what sits inside each one.

**[2:20] Slide 7 - The reference stack**
> Concretely, we build those five layers on AWS, Snowflake and Databricks. Databricks builds it, Snowflake governs it, AWS serves it in real time. This is the stack the Tier-1 institutions have already converged on, so we are not asking you to bet on anything unproven.

**[2:40] Slide 8 - Real-time, sub-98ms (ROTATE THE MODEL)**
> The hardest promise we make is speed: a personalized decision in under ninety-eight milliseconds.
>
> *[Click the model, drag slowly along the pipeline.]*
>
> Watch the path. A live event, buffered in Kafka, features computed in Flink, read from an online store in under a millisecond, scored, and a decision returned.
>
> *[Let it turn.]*
>
> End to end, about thirty-five milliseconds at the ninety-ninth percentile. That headroom is what lets us add governance and still stay real-time.

**[3:15] Slide 9 - Why the stack holds at scale**
> And it holds at scale, tens of millions of customers, because the hot path uses a key-value store with predictable single-digit-millisecond reads, and because we colocate the model, the rules and the data in one region. The latency does not degrade as you grow.

**[3:35] Slide 10 - The frontier: the agentic loop (ROTATE THE MODEL)**
> This is the frontier, and where we go beyond the current standard: an agentic loop.
>
> *[Click the model, drag slowly around the ring.]*
>
> The agent perceives, reasons, acts and observes. It calls tools through a governed gateway, with memory on the left and, critically, a human escalation path at the top.
>
> *[Let it turn.]*
>
> It acts autonomously on the routine and hands off to a person whenever policy demands. Bajaj closes loans this way today.

**[4:10] Slide 11 - Why the stack for agentic data**
> And it is safe by design. We keep personal data out of the model, we fence the tools the agent can touch, and every action it takes is logged and auditable. Autonomy without recklessness.

**[4:30] Slide 12 - The model toolkit**
> Underneath, eight model patterns cover almost every use case you have: propensity, uplift, recommendation, fraud graphs, grounded language models, and agents. You do not need a hundred models. You need these eight, done well.

**[4:50] Slide 13 - The differentiator: governance**
> This is our real differentiator. Governance is not a bolt-on. Thirteen regulatory regimes across your regions, satisfied by one thing: an audit log that captures the reason, the fairness check and the data behind every decision. A regulator can ask about any decision, and you will have the answer.

**[5:10] Slide 14 - Proof we draw from**
> These are the marquee references we learn from, and the one lesson each teaches. Capital One on experimentation, DBS on scale, and Goldman's Marcus on why distribution matters more than a slick app. We are not theorizing. We stand on what worked, and we design around what failed.

**[5:30] Slide 15 - Not just meeting the standard**
> So here is how we do not just meet the standard, but surpass it. Five ways: real-time by default, causal targeting rather than plain propensity, agentic on the routine, governance shipped with every decision, and one brain across every channel.

**[5:50] Slide 16 - What we build first**
> What we build first is a demo. Lean, but structurally the real thing. The same five layers, running on a laptop, proving a sub-ninety-eight-millisecond decision with a live audit row.

**[6:05] Slide 17 - From demo to production**
> And the demo becomes production by swapping boxes, not by rewriting. Postgres becomes Snowflake and Databricks. Redis becomes the cloud online store. Same interfaces, same structure. No re-architecture.

**[6:20] Slide 18 - The plan**
> The plan delivers value early. A working demo in twelve weeks, the first production sub-vertical inside a year, measured against a real holdout so every number is causal.

**[6:35] Slide 19 - The economics**
> This is where the two-hundred-million to one-billion comes from, built bottom-up, sub-vertical by sub-vertical. Not a slogan. Arithmetic your CFO can check.

**[6:50] Slide 20 - The promise**
> So the promise is simple. One architecture that surpasses the current standard on speed, on autonomy and on governance. Proven small, and scaled by swaps. We would love to build it with you. Thank you.

**[~7:00] End.**

---

## If you need the 3-minute cut

Keep slides 1, 2, 6 (rotate), 8 (rotate), 10 (rotate), 15 and 20. Drop the rest. That preserves the stakes, the three models, the differentiation and the ask.

## Quick recovery lines (if you fumble)

- Lost your place: "The thread through all of this is one engine, five layers, every decision governed."
- Model will not rotate: keep talking, describe it from the labels, move on. Do not stop to fight the software.
- Asked a hard question mid-record: "Good question, let me come back to that at the end," and continue.
