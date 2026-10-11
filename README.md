<p align="center"><img src="assets/logo.png" width="96" alt="FridgeOut logo" /></p>

<h1 align="center">FridgeOut · Recipe Wizard</h1>
<p align="center"><strong>Cook with what you have.</strong></p>
<p align="center">A mobile product that turns the ingredients you already have into cooked meal ideas.<br />Product showcase, engineering case study and selected educational examples.</p>

<p align="center">
  <a href="#from-fridge-to-dinner">Product</a> ·
  <a href="#engineering-case-study">Engineering</a> ·
  <a href="docs/INTERVIEW_GUIDE.zh-CN.md">面试讲解</a> ·
  <a href="docs/ARCHITECTURE.md">Architecture</a> ·
  <a href="docs/AI_WORKFLOW.md">AI workflow</a> ·
  <a href="#run-the-public-examples">Run examples</a>
</p>

<p align="center"><img src="assets/screenshots/01-kitchen.png" width="290" alt="FridgeOut kitchen home screen" /></p>

## From fridge to dinner

Take or upload a fridge photo, review what the model recognized, and confirm names, quantities and units. Your confirmed kitchen inventory becomes the context for up to five cooked recipes that fit your dietary preferences and available time.

<p align="center">
  <img src="assets/screenshots/02-confirm-ingredients.png" width="230" alt="Review recognized ingredients" />
  <img src="assets/screenshots/02-confirm-save.png" width="230" alt="Correct and confirm a scan" />
  <img src="assets/screenshots/03-inventory.png" width="230" alt="Confirmed kitchen inventory" />
</p>
<p align="center"><sub>Review the photo · Confirm the ingredients · Find something to cook</sub></p>

## Keep the good ideas

Explore recipes with dish images and cooking steps. Save a favorite to revisit later. Generated images are stored and reused; opening the app again does not require another model generation for an already saved image. Offline ingredient and favorite deletions synchronize when the app reconnects and runs in the foreground.

<p align="center">
  <img src="assets/screenshots/04-recipes.png" width="230" alt="Recommended cooked recipe" />
  <img src="assets/screenshots/04-more-recipes.png" width="230" alt="More meal ideas" />
  <img src="assets/screenshots/05-favorites.png" width="230" alt="A saved favorite recipe" />
</p>
<p align="center"><sub>Explore ideas · Read the instructions · Keep a favorite</sub></p>

## Made for your kitchen

Choose dietary preferences and a maximum cooking time. A free allowance and two monthly subscription tiers make paid AI usage explicit. Purchasing uses Apple in-app purchases with RevenueCat subscription verification.

<p align="center">
  <img src="assets/screenshots/06-your-plan.png" width="260" alt="Account and upgrade screen" />
  <img src="assets/screenshots/07-preferences.png" width="260" alt="Dietary and cooking-time preferences" />
</p>

**Release status:** iOS distribution and purchase validation are in progress as of October 2026. This repository does not claim an approved App Store release, paying customers or production-scale usage. Screenshots may show a development account; they are product demonstrations, not evaluation evidence. Dish images are AI illustrations, not photos of tested meals.

## Engineering case study

The interesting problem is making a paid AI feature trustworthy enough to use repeatedly. A fluent recipe is not sufficient: it must respect a real user's inventory, survive unreliable mobile networks, avoid duplicate image spending, and keep account data isolated.

The project combines a TypeScript / React Native app built with Expo, a Python / FastAPI backend, a bounded LangGraph workflow, MCP data tools, Supabase authentication/database/storage, OpenAI multimodal and image APIs, and Apple / RevenueCat billing. I developed it with AI-assisted tooling; the interview material focuses on design decisions, code behavior and verification rather than claiming every line was written without assistance.

| Engineering problem | Implemented approach | Discuss the trade-off |
| --- | --- | --- |
| Photo recognition can misidentify quantities | Structured recognition followed by explicit human confirmation | More user effort in exchange for a controlled inventory write |
| Generated recipes can invent ingredients | Deterministic constraints, a separate model evaluation call and bounded regeneration | A model judge adds coverage but is not an independent proof of correctness |
| Agent tools could access the wrong account | Verified identity propagation plus database row-level security | Tool separation adds a process boundary and operational overhead |
| Reopening the app can cause repeated image work | Stored images, database leases, signed URLs and local image caches | Coordination and cleanup become part of the feature |
| Offline deletion can reappear after refresh | Account-scoped persistent tombstones and a retry queue | Eventual consistency; the app must run to synchronize |
| AI retries can overspend | Persistent idempotency, atomic budget reservations and server-verified allowances | Conservative reservations can reject work before the actual bill is known |

### Read the technical story

- [Architecture](docs/ARCHITECTURE.md): system boundaries, identity, storage and request flows.
- [AI workflow](docs/AI_WORKFLOW.md): LangGraph, MCP, guardrails, the model judge and offline evals.
- [Engineering challenges](docs/ENGINEERING_CHALLENGES.md): failure scenarios, decisions and limits.
- [Validation and evidence](docs/VALIDATION.md): what the checks establish and what they do not.
- [面试讲解提纲](docs/INTERVIEW_GUIDE.zh-CN.md): 90 秒介绍、5 分钟讲解和常见追问。
- [Public repository scope](docs/PUBLIC_SCOPE.md): what is shared and what remains in the product repository.

### Run the public examples

Python 3.11+; no API keys, cloud account or third-party packages required:

```bash
python3 -m examples.recipe_constraints
python3 -m examples.offline_deletions
python3 -m unittest discover -s tests -v
```

These are deliberately simplified, runnable teaching examples inspired by the product. They demonstrate [cumulative inventory constraints](examples/recipe_constraints.py) and [account-scoped offline deletion](examples/offline_deletions.py). They do **not** implement the complete app, call a live model or reproduce the production security boundary. Example output is fixture evidence, not a live-model quality benchmark.

## About this repository

FridgeOut's complete application, prompts, billing implementation, deployment configuration and database migrations are maintained separately. This repository starts with a fresh Git history and contains only documentation, product assets and selected educational code. It is not an installable copy of the paid app.

Questions: [bowenivy0@gmail.com](mailto:bowenivy0@gmail.com). [Privacy policy](https://fridgechef-api-0lcg.onrender.com/privacy).

Copyright © 2026 Bowen Li. All rights reserved. See [NOTICE](NOTICE).
