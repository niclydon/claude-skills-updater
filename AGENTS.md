# AGENTS.md

Instructions for AI coding agents (Claude Code, Codex, Cursor, etc.)
working in or with this repository.

This file is the canonical neutral guide. Tool-specific adapters
(`CLAUDE.md`, etc.) defer to it.

## What this repo is

`claude-skills-updater` is a small, stdlib-only harness that:

1. Catalogs every Claude Code skill the user has installed
   (`~/.claude/skills/<name>/SKILL.md` and plugin-bundled skills under
   `~/.claude/plugins/cache/...`).
2. Mines the user's local Claude Code conversation history at
   `~/.claude/projects/*.jsonl` for recurring task patterns.
3. Cross-references the two and produces a ranked list of candidate
   *new* skills the user should author.

It does NOT author skills, install plugins, or modify
`~/.claude/skills/`. It is read-only against the user's Claude Code
install — its only output is files inside this repo.

## If the user just handed you this repo URL

They almost always want one of three things. Pick by intent:

### Intent A — "set this up for me" / "run a pass"

Execute the four-step loop:

```bash
git clone https://github.com/niclydon/claude-skills-updater
cd claude-skills-updater

python3 scripts/inventory.py            # snapshot installed skills
python3 scripts/extract-prompts.py      # mine ~/.claude/projects/*.jsonl
./scripts/orchestrate.sh --label initial   # call `claude -p` for synthesis
```

The recommendation file lands at
`recommendations/<today>-initial.md`. Show its contents to the user
and let them pick which skills to author.

If `claude` is not on `$PATH`, run `./scripts/orchestrate.sh --dry-run`
instead — it prints the synthesis prompt + input paths so the user can
paste it into any chat surface.

### Intent B — "what would you recommend I run / how does this work?"

Don't run anything yet. Walk them through the four steps in
`docs/process.md`, point out the privacy notes (the `prompts/`
directory is gitignored because the corpus contains personal data),
and ask whether they want to proceed.

### Intent C — "extend this" / "modify the synthesis prompt"

Three knobs they'll likely want:

1. **Synthesis prompt** — the heredoc inside `scripts/orchestrate.sh`.
2. **Noise filter** — `NOISE_PREFIXES` in `scripts/extract-prompts.py`
   (drops slash-command echoes, system reminders, compaction
   summaries).
3. **Catalog parser** — `scripts/inventory.py` parses SKILL.md
   frontmatter with two regexes (`name:` and `description:`). Add
   fields by extending those, but keep stdlib-only.

## Hard rules

- **Stdlib-only Python.** No `pip install` for `inventory.py`,
  `catalog-diff.py`, or `extract-prompts.py`. If you find yourself
  reaching for PyYAML or pandas, redesign.
- **`prompts/` is never committed.** It contains the user's raw
  conversation history. The `.gitignore` already excludes it; do not
  override.
- **Never write into `~/.claude/skills/` from these scripts.** This
  harness suggests skills, it does not author them. If the user wants
  to author a recommended skill, point them at the
  `superpowers:writing-skills` skill (a TDD-style authoring workflow
  bundled with the `superpowers` plugin) or guide them manually.
- **Same-day re-runs are idempotent.** All scripts overwrite their
  outputs in place when re-run. Preserve this property.

## File layout

```
catalogs/             # committed; one JSON file per refresh + latest.json
prompts/              # gitignored; TSV of real user prompts
recommendations/      # committed; one MD file per synthesis pass
scripts/
  inventory.py        # build a catalog snapshot
  catalog-diff.py     # diff two snapshots
  extract-prompts.py  # mine JSONL transcripts
  orchestrate.sh      # call `claude -p` to synthesize recommendations
docs/
  process.md          # detailed workflow
  skill-anatomy.md    # SKILL.md frontmatter contract
```

Read `docs/process.md` before making non-trivial changes. It contains
the rationale for the four-step structure and the trade-offs that
shaped each script.

## Platform notes

| Platform | Status |
|---|---|
| macOS | Tested, works. |
| Linux | Tested, works. |
| Windows native | Untested. Python scripts likely portable; `orchestrate.sh` is bash — use WSL or port to PowerShell. |
| WSL | Likely fine; same as Linux if Claude Code is in WSL. |

## Common pitfalls

- **Empty catalog after `inventory.py`.** Means `~/.claude/skills/`
  and `~/.claude/plugins/cache/` are both empty or absent. Confirm the
  user has Claude Code installed and has activated at least one
  plugin or authored at least one personal skill.
- **`extract-prompts.py` outputs zero rows.** Means
  `~/.claude/projects/` is empty. Either Claude Code is freshly
  installed (no transcript history), or the user is on a non-default
  install path. Pass `--projects-dir <path>` to override.
- **`orchestrate.sh` errors with `claude: command not found`.** The
  user doesn't have Claude Code on `$PATH`. Use `--dry-run` and have
  them paste the prompt elsewhere, OR add the binary to PATH first.

## When NOT to touch this repo

- The user wants to *author* a new skill. That work happens at
  `~/.claude/skills/<new-name>/SKILL.md`, not here.
- The user wants to install a plugin. Use the Claude Code plugin
  manager.
- The user is debugging a specific skill's behavior. The skill body
  lives in their Claude install, not in this repo.

## Quick verification

After any change to `scripts/`, run:

```bash
python3 scripts/inventory.py --no-write   # smoke-test parser
python3 scripts/extract-prompts.py --no-write | head -5
./scripts/orchestrate.sh --dry-run        # confirm prompt assembly
```

All three should exit 0 and produce sensible output without writing
new files.
