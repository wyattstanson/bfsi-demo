# Aria, Full Walkthrough Script

A complete, click-by-click script for demoing the live site. Stage directions are in **[brackets]**, the words to say are in quotes. Target run time is 12 to 15 minutes, with a 6-minute cut marked inline. Pause after every number.

---

## Before you start (pre-flight, do this off-screen)

- **URL:** `https://aria-bfsi-platform.onrender.com` (free tier, so open it 60 seconds early to wake the server).
- **Have ready:** the customer login `Aryansh` / `Aryansh`, and the Engine Room passcode `Aryansh@Tredence`.
- **Zoom the browser to about 100 to 110%,** theme toggle in the top right if the room is bright, and close other tabs.
- **One-line framing to open with:** this is one real-time personalization engine, shown through five stakeholders' eyes, and it returns a governed decision in under ninety-eight milliseconds.

---

## [0:00] The landing page, set the thesis

**[Land on `/`. Do not rush past it.]**

> "Personalization in banking is usually a slogan. Aria is the working engine. The same brain serves five very different people: a customer, an advisor, an executive, a regulator, and the engineer who has to keep it honest. Let me show you all five, and then open the hood."

**[Point at the five mode cards, then at the sidebar once you enter.]**

> "Notice the navigation. Each view is its own page with its own URL, so anything here is a link you can send. Watch the address bar as we go."

**[Click "Explore the platform" or the Concierge card.]**

---

## [1:00] Concierge, what the customer feels  (URL: `/concierge`)

**[Sidebar now shows on the left. You are on Concierge. Point at the URL: it changed to `/concierge`.]**

> "This is the customer. No dashboards, no scores, just a helpful moment. Pick a profile and press Show my moment."

**[Select a profile, click "Show my moment". A friendly card appears.]**

> "That card is a next-best-action decision, rendered as a human moment. Behind it, the engine scored every eligible action by expected value, applied the rules, and picked the winner, in a few milliseconds. The customer never sees the machinery. They just feel understood."

**[Now move to Ava, the chat on the right. Type:]** `how do I start investing`

> "This is Ava. She is a personalization expert who can actually hold a conversation. She is deterministic and offline by default, so she is fast and private, and she upgrades to a full Claude model when an API key is present."

**[Change the "Area" dropdown from Any to Payments. Point at the sample chips changing.]**

> "The suggestions adapt to the area of finance you care about. Switch to Payments and the prompts change to fraud, agentic commerce, card-linked offers."

**[Click the History button at the top of the chat.]**

> "Every conversation is saved to the cloud, tied to the customer, with a New chat button and one-click restore. Sign in on another device and your history follows you. It also works offline with a local fallback."

**[Optional flex: type something casual like]** `yo gang` **[to show she greets naturally, then]** `i feel behind everyone my age` **[to show emotional intelligence.]**

> "She reads tone. Slang gets a warm hello, and a stressed message gets empathy first, advice second."

**[6-minute cut: from here, jump straight to the Engine Room at 7:30.]**

---

## [3:00] Co-pilot, the advisor  (URL: `/co-pilot`)

**[Click Co-pilot in the sidebar. URL becomes `/co-pilot`.]**

> "Same engine, different stakeholder. This is the relationship co-pilot. It drafts a ready-to-use brief and the talking points for the next client conversation, and it will speak them aloud."

**[Pick a client, let the brief render. Point at the recommended action, the reason codes, and the talking points.]**

> "This is the Aladdin Auto-Commentary pattern. The human keeps the relationship, the model does the preparation, and advisor productivity goes up twenty-five to forty percent. Notice it shows the same decision the customer felt, now with the reasons exposed."

---

## [4:15] Control Tower, the executive  (URL: `/control-tower`)

**[Click Control Tower. URL becomes `/control-tower`.]**

> "The leader does not want a chatbot. They want the book of decisions. Value created, decisions served, latency, fairness, at a glance."

**[Point at the headline numbers and the decision stream.]**

> "Every one of these is a real decision from the same engine, with its latency and fairness flag. This is how you turn a personalization program into a P&L line a CFO can check."

---

## [5:15] Assurance, the regulator  (URL: `/assurance`)

**[Click Assurance. URL becomes `/assurance`.]**

> "This is the view most vendors do not show you. The regulator's view. Pick any decision and it is fully explained."

**[Let the SHAP force plot render. Point at the contributing factors and the audit entry.]**

> "This is a SHAP force plot: exactly which factors pushed the decision up or down, and by how much. Every decision carries an audit row with reason codes and a fairness check. Governance is not a report we run later. It runs inside the decision, and no response is returned without its audit trail."

---

## [7:30] Engine Room, under the hood  (URL: `/engine-room`, passcode `Aryansh@Tredence`)

**[Click Engine Room. It is locked. Enter the passcode.]**

> "This is for the engineer who has to trust it in production. Everything you just saw, proven."

### The pipeline

**[Point at the five-layer strip. Click "Run a decision through the pipeline".]**

> "Five layers: data, features, models, decisioning, governance. Watch a single decision flow through all five, live. The whole thing lands under ninety-eight milliseconds, and that budget includes the fairness and explainability work."

### Why the stack is built this way

**[Point at each panel as you say it. This is the tech heart of the demo.]**

> "Every choice here is a latency, governance, or cost decision.
> Features come from a key-value store, not a database join, because a KV read is single-digit milliseconds and a join has a long tail.
> We serve tree models, XGBoost and LightGBM, not deep nets in the path, because trees score in microseconds and their reason codes are exact, which the regulator wants.
> Decisioning is a LinUCB bandit with the matrix inverse cached, so a live decision does zero matrix inversions.
> And the audit write is off the hot path, batched every two hundred and fifty milliseconds, so a decision does zero blocking I/O."

### Scale

**[Click "Run a 120-request burst". Point at the p99 and per-core rate.]**

> "Decisioning is stateless, so throughput is CPU-bound and scales linearly. Per-core rate times cores times autoscaled replicas on EKS gets you past a million decisions a second. A million customers never touch memory at once."

### Live data and topology

**[Point at the CDC event stream, the live database counts, the audit tail, then the topology table.]**

> "This is a real streaming feed, a real database, and a live tail of the audit log. And here is the production topology: the exact same five layers map onto AWS for the substrate, Databricks for the ML and streaming engine, and Snowflake for governed reporting. The demo becomes production by swapping boxes, not by rewriting."

### The agentic loop

**[Scroll to the agentic trace. Set a goal like "I want a pre-approved loan of 50000" and run the agent.]**

> "And this is the agentic loop: perceive, reason, act, observe, with a human-in-the-loop stop for anything above a policy threshold. Autonomy on the routine, a human when the stakes are high."

### Industry reference

**[Scroll to the Industry Reference panel.]**

> "Finally, so this is not just our opinion, here is how the majors actually build it. Visa, Mastercard, Fiserv, PayPal, Stripe, JPMorgan, Capital One, their AI, data, and cloud layers, their latency posture, and their EU AI Act exposure. Where the internals are not public, we mark them not public, not absent. Being honest about the gaps is what makes the rest credible."

**[Point at the sub-98ms budget bar and the layers.]**

> "The blueprint sums to sixty-five milliseconds of mandatory hot path against a ninety-eight millisecond budget. Governance, vector, and training layers are asynchronous and excluded. It is a plan a client's own architects can check."

---

## [11:30] Close

> "So that is Aria. One engine, five stakeholders, sub-ninety-eight-millisecond governed decisions, and a straight line from this demo to production on a cloud a client already trusts. Every choice in the stack answers to speed, governance, or cost, and every one of them is defensible in front of a risk committee. That is what we would build with you."

---

## If the room pushes back (keep these ready)

- **"Is the sub-ninety-eight milliseconds real with governance on?"** Yes. Governance is cached and the audit write is off the hot path. The burst test shows the live p99.
- **"Why not deep learning everywhere?"** Latency and explainability. Trees score in microseconds with exact reason codes; deep nets only where the accuracy pays for the milliseconds.
- **"Why three clouds?"** They are not competing. AWS is the substrate, Databricks is the ML engine, Snowflake is the governed SQL layer.
- **"What about the EU AI Act?"** This is Annex III high-risk. Transparency obligations are live now, the high-risk deadline is December 2027. Governance is built in, so we are ahead of it.
- **"Is my data safe?"** PII never reaches a model. Names and identifiers stay in a governed ledger; the hot path and every model payload carry ids and non-PII features only, and a test enforces it.

## If something breaks (recovery lines)

- **Server is cold or slow:** "Free-tier instance waking up, one second." Keep talking about the architecture while it loads.
- **A panel does not render:** refresh the page (state is server-side), or narrate the intent: "This normally shows the live audit tail."
- **Ava gives a thin answer:** "She is the offline brain right now, deterministic and private. With a model key she is fully conversational." Then ask her something squarely in scope.

## Quick reference card

| View | URL | One line |
|---|---|---|
| Landing | `/` | One engine, five stakeholders |
| Concierge | `/concierge` | The customer's moment, plus Ava |
| Co-pilot | `/co-pilot` | The advisor's auto-commentary brief |
| Control Tower | `/control-tower` | The executive's book of decisions |
| Assurance | `/assurance` | The regulator's SHAP and audit |
| Engine Room | `/engine-room` | Under the hood, plus the industry reference |

Login `Aryansh` / `Aryansh`. Engine Room passcode `Aryansh@Tredence`.
