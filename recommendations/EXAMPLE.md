# EXAMPLE — what a recommendation pass looks like

This is a synthetic example showing the shape of a real
recommendations file. Your actual output from `./scripts/orchestrate.sh`
will be specific to your prompt history.

---

# 2026-01-15 — quarterly pass

Source corpus: ~3,800 user prompts from 12 weeks of Claude Code work.
Catalog: 8 user skills + 50 plugin skills.

## Top recommendations (ranked)

### 1. db-migration-runner — drive Postgres migrations through the project's standard flow
**Trigger:** "run the next migration", "apply migration N", "rollback
the last migration".
**What it does:** Reads the project's migration directory convention,
applies in order, verifies, updates the migration tracking table,
documents the change in CHANGES.md.
**Why it's a gap:** 38 migration-related prompts across 4 projects.
Every project uses a slightly different flow; rediscovered each time.
**Leverage:** Saves 5–10 min per migration; prevents the "wrong
DATABASE_URL" class of mistakes.

### 2. testflight-build — iOS Xcode + altool upload via SSH to build host
**Trigger:** TestFlight build, Xcode signing/keychain errors over SSH.
**What it does:** Drives the canonical SSH-to-build-host flow: unlock
keychain over `-t`, list signing identities, build, upload via altool.
**Why it's a gap:** Same errors rediscovered every cycle: "User
interaction is not allowed", "Pseudo-terminal will not be allocated".
**Leverage:** High; build cycles are weekly and friction is
predictable.

### 3. multi-model-bench — promptfoo benchmark across multiple local models
**Trigger:** "benchmark X vs Y", "test against draft + base", "3-panel
tmux tail".
**What it does:** Generates promptfoo config matrix, wires telemetry,
launches the standard tmux layout, outputs comparable
TTFT/TPS/correctness.
**Why it's a gap:** Every benchmark request takes the same shape;
plumbing redone each time.
**Leverage:** Encodes the harness so each benchmark is one prompt, not
30 minutes of setup.

(…8–15 candidates total in a real pass…)

## Skipped (already covered or too thin)

- Generic "deploy / verify" — already covered by an installed
  deployment skill.
- "commit and push" alone — too small to skill.
- One-shot retirement work — not recurring.

---

## Reading this file

Each candidate has:

- **Name + tagline** — short identifier.
- **Trigger** — what the user actually says when this skill should
  activate.
- **What it does** — 2–3 lines on the workflow.
- **Why it's a gap** — evidence from the corpus (counts, example
  prompt patterns).
- **Leverage** — how often it comes up + why a skill beats winging it.

Pick the top 3–6 that match how you work, then author them via your
preferred skill-authoring workflow (we recommend
`superpowers:writing-skills`). Don't build all of them — many
candidates are correct in principle but rarely worth the maintenance.

After authoring, re-run `inventory.py` so the new skill appears in
the catalog and won't be re-recommended next pass.
