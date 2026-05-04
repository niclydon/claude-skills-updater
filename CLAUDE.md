# CLAUDE.md

Guidance for Claude Code when working with this repo.

**See [`AGENTS.md`](AGENTS.md) for the canonical guide.** Everything an
agent (any agent) needs to use, run, or extend this repo lives there.

## Claude Code specifics

A few things `AGENTS.md` doesn't cover that are Claude Code-specific:

- **Skill discovery.** This harness reads from `~/.claude/skills/` and
  `~/.claude/plugins/cache/*/<plugin>/<version>/skills/`. If Claude
  Code's install layout changes upstream, update the path constants
  in `scripts/inventory.py`.
- **Synthesis driver.** `scripts/orchestrate.sh` calls `claude -p`
  (the headless Claude Code mode). It passes `--add-dir` and
  `--max-budget-usd` to scope the agent and cap spend.
- **Skill authoring follow-up.** When the user picks candidates from
  a recommendations file and wants to author them, suggest the
  `superpowers:writing-skills` skill — it enforces a TDD-style
  workflow (baseline-fail → write SKILL.md → confirm compliance →
  refactor).

Everything else — process, conventions, hard rules, platform notes,
common pitfalls — is in `AGENTS.md`.
