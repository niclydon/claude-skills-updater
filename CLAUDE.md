# CLAUDE.md

Guidance for Claude Code when working with this repo.

# claude-skills-updater agent notes

This repo is a catalog + recommendation engine for Claude Code skills.
It does not author or install skills.

## What it owns

- `catalogs/` — versioned snapshots of every installed skill. Committed.
- `scripts/inventory.py` — build a snapshot from `~/.claude/skills/` and
  `~/.claude/plugins/cache/*/<plugin>/<version>/skills/`.
- `scripts/catalog-diff.py` — diff two snapshots.
- `scripts/extract-prompts.py` — walk `~/.claude/projects/*.jsonl` and
  emit a TSV of real user-typed prompts.
- `scripts/orchestrate.sh` — drive `claude -p` to produce
  `recommendations/<today>-<label>.md`.
- `docs/process.md`, `docs/skill-anatomy.md` — master docs.
- `recommendations/` — ranked candidate-skill writeups.

## What it does NOT own

- Skill files. They live at `~/.claude/skills/<name>/SKILL.md` (or in
  plugin packages).
- Plugin installation.
- The skill authoring workflow itself (see `superpowers:writing-skills`).

## Common workflows

### Refresh catalog
```
python3 scripts/inventory.py
```
Writes `catalogs/<today>.json` and updates `catalogs/latest.json`.
`--no-write` prints to stdout. Same-day re-runs overwrite in place.

### See what changed
```
python3 scripts/catalog-diff.py
```
Defaults to latest vs the most recent prior snapshot whose contents
differ. Pass two paths to override. Add `--json` for machine output.

### Mine the prompt corpus
```
python3 scripts/extract-prompts.py
```
Walks `~/.claude/projects/*.jsonl` in parallel, filters to real
user-typed prompts (drops sidechain turns, tool results, system
reminders, slash-command echoes, compaction summaries), writes
`prompts/<today>.tsv`. `prompts/` is gitignored.

### Run a recommendation pass
```
./scripts/orchestrate.sh --label <name>
```
Calls `claude -p` with both `catalogs/latest.json` and
`prompts/latest.tsv`. Writes `recommendations/<today>-<label>.md`.

`--dry-run` prints the prompt without calling claude. `--refresh`
rebuilds catalog and prompts first.

## Convention

- Stdlib-only Python; no `pip install` for `inventory` / `diff` /
  `extract`.
- Same-day re-runs are idempotent.
- `catalogs/` and `recommendations/` ARE committed; `prompts/` is
  NEVER committed (treat the corpus like raw conversation logs).
- Never write into `~/.claude/skills/` from these scripts.

## How `inventory.py` finds skills

Two roots:
1. `~/.claude/skills/<name>/SKILL.md` — user-level (highest priority).
2. `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/skills/<name>/SKILL.md`
   — plugin-bundled.

Each entry is `{name, source, description, path}` parsed from the
SKILL.md frontmatter. `source` is `user` or `plugin:<plugin-name>`.
User-level skills win on name collision.

## Platform notes

- macOS + Linux confirmed working.
- Windows (native) untested. The Python scripts should be portable; the
  bash orchestrator is not. Use WSL or port `orchestrate.sh` to
  PowerShell.
- The JSONL transcript path on Windows is presumed to be
  `%USERPROFILE%\.claude\projects\` — pass `--projects-dir` if it
  differs.
