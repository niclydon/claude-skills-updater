# CHANGES

Documentary log of significant changes. Group by date. Lead with
decisions and reasons; include specifics second.

## 2026-05-04 — initial public release

`claude-skills-updater` published at
`https://github.com/niclydon/claude-skills-updater` as a public,
MIT-licensed harness for cataloging Claude Code skills and recommending
new ones based on the user's local conversation history.

The repo is a deliberate spinoff of a personal one (`skills-updater`)
that grew out of a one-off "look through all my JSONL files and
recommend new skills" question. Once the workflow worked end-to-end and
turned out to be re-usable monthly, the case for a generic public
version became obvious — every Claude Code user accumulates the same
kind of recurring task patterns and would benefit from the same kind of
periodic gap analysis.

### What shipped

The four-script harness, identical to its private parent:

- `scripts/inventory.py` walks `~/.claude/skills/<name>/SKILL.md` and
  `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/skills/<name>/SKILL.md`,
  parses YAML frontmatter (`name:` + `description:`) via two stdlib
  regexes, and writes `catalogs/<today>.json` plus
  `catalogs/latest.json`.
- `scripts/catalog-diff.py` reports added / removed / description-
  changed / source-changed skills between any two snapshots.
- `scripts/extract-prompts.py` walks `~/.claude/projects/*.jsonl` in a
  thread pool, filters to real user-typed prompts (drops sidechain
  turns, tool results, slash-command echoes, system reminders,
  compaction summaries), and writes a TSV. The corpus is gitignored —
  it is personal data.
- `scripts/orchestrate.sh` calls `claude -p` with both inputs plus a
  fixed instruction prompt asking for ranked candidate skills.

### Three design choices worth recording

1. **Stdlib-only Python.** No PyYAML, no pandas, no `pip install`.
   The cost of a dependency tree on a tool that should "just work
   after `git clone`" is too high. Two regexes is enough to parse the
   `name:` and `description:` we care about; complex YAML still
   parses without us caring about the rest.
2. **JSONL crawler, not DB query.** A precursor harness for MCP tools
   (`mcp-updater`) reads conversation signals from a local Postgres
   gold layer. This one deliberately reads from the JSONL transcripts
   on disk so the harness has zero infrastructure dependencies. A
   user with only Claude Code installed can run a recommendation
   pass — no DB, no extra services.
3. **Catalog committed; prompts gitignored; recommendations
   committed.** The catalog is metadata about installed skills (safe).
   The prompt corpus is conversation history (sensitive — never
   committed). The recommendations are derived analysis, but they may
   cite patterns from the corpus, so authors should review before
   publishing forks of this repo with their own recommendations
   files.

### AGENTS.md as the canonical entry point

When someone pastes the repo URL into Claude Code, Codex, or Cursor,
they almost always want one of three things: run a pass, understand
what this is, or extend the harness. `AGENTS.md` maps each of those
intents to concrete commands, surfaces the hard rules (stdlib-only,
prompts/ never committed, never write into `~/.claude/skills/`), and
calls out platform caveats (macOS + Linux confirmed; Windows native
untested; bash needed for `orchestrate.sh`).

`CLAUDE.md` defers to `AGENTS.md` rather than duplicating it. Same for
the README — it has a one-paragraph pointer near the top so a human
landing on the GitHub page can route either themselves or their agent
to the right file.

### What this repo intentionally does NOT do

- Author skills. The recommendations file is a triage queue, not
  generated `SKILL.md` files. Pair this harness with the official
  `superpowers:writing-skills` skill (in the `superpowers` plugin) for
  the actual authoring workflow — it enforces a TDD-style baseline-
  fail → write → confirm → refactor cycle.
- Install plugins. Use the Claude Code plugin manager.
- Modify `~/.claude/skills/`. The harness is read-only against the
  user's install — its only output is files inside this repo.

### Initial commits

Three commits at launch:

- `b045018` initial commit: harness for cataloging skills + recommending new ones
- `3fc89ec` genericize naming examples in docs/skill-anatomy.md
- `098ce2b` add AGENTS.md as canonical agent guide; CLAUDE.md defers to it

Default branch is `master`. PRs and issues open. Repo description:
*"Catalog + recommendation engine for Claude Code skills — mines your
local conversation history for recurring task patterns and suggests
new skills to author."*
