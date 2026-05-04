# claude-skills-updater

A small, opinionated catalog + recommendation engine for [Claude Code]
skills. It answers the recurring question:

> *Given everything I've actually asked Claude Code to do, what new
> skills should I add?*

It does that by mining your local `~/.claude/projects/*.jsonl`
conversation history for recurring task patterns, cross-referencing
against the skills you already have installed, and producing a ranked
shortlist of candidate new skills you can author.

No external services. Stdlib-only Python. Calls `claude -p` for the
synthesis step (optional — you can run dry-run and read the prompt
yourself).

[Claude Code]: https://docs.claude.com/claude-code

## Why

Without a catalog and a prompt corpus, every "what skills should I add?"
question forces a full rediscovery: walk every JSONL transcript,
re-summarize the existing skill set, eyeball patterns, write
recommendations. Doing it once is enlightening. Doing it monthly is
tedious. This repo turns the workflow into four small commands.

## Layout

```
catalogs/
  YYYY-MM-DD.json     # daily snapshot of every installed skill
  latest.json         # copy of the most recent snapshot
prompts/              # gitignored — extracted user prompts may contain PII
  YYYY-MM-DD.tsv      # cwd<TAB>timestamp<TAB>prompt (truncated to 500 chars)
  latest.tsv
scripts/
  inventory.py        # catalog every installed skill
  catalog-diff.py     # diff two snapshots
  extract-prompts.py  # mine ~/.claude/projects/*.jsonl for real user prompts
  orchestrate.sh      # drive `claude -p` to produce a fresh recommendations file
docs/
  process.md          # master process doc
  skill-anatomy.md    # what a SKILL.md looks like; frontmatter contract
recommendations/
  YYYY-MM-DD-<label>.md   # ranked candidate skills for a given pass
  README.md
```

## The four-step loop

```bash
# 1. Snapshot what's installed
python3 scripts/inventory.py

# 2. See what changed since last snapshot
python3 scripts/catalog-diff.py

# 3. Mine the prompt corpus
python3 scripts/extract-prompts.py

# 4. Generate ranked candidate skills
./scripts/orchestrate.sh --label initial
```

Step 4 calls `claude -p`. If you'd rather not, use `--dry-run` to print
the synthesis prompt + inputs and run it yourself in any chat surface.

## Example output

A recommendations file looks like this (one of many ranked entries):

```markdown
### narrative-docs-update — heavy documentary-grade doc/CHANGES updates
**Trigger:** "update docs", "narrative update", "heavy narrative doc
update", often chained with "commit and push" / "commit and deploy".
**What it does:** Loads project doc-style guides, updates plan docs,
appends chronological story blocks to CHANGES.md, syncs cross-project
references, gates commit on explicit ask.
**Why it's a gap:** 147 hits across ~30 projects. No existing skill
covers it.
**Leverage:** Highest-frequency repeated task in the corpus.
```

The synthesis prompt asks for 8–15 ranked candidates plus a "skipped
(already covered)" section. You then pick the top N and author them
using your preferred skill-authoring workflow.

## Privacy

`prompts/` is **gitignored by default**. The corpus is your raw
conversation history — treat it like logs. The catalog (just skill
names + descriptions + paths) is fine to commit. Recommendations are
fine to commit but may cite patterns derived from your prompts; review
before publishing.

## What this repo does NOT do

- Author skills. The recommendations file is a triage queue, not
  generated `SKILL.md` files. (Pair with the `superpowers:writing-skills`
  skill for authoring.)
- Install plugins. Use the Claude Code plugin manager.
- Modify your `~/.claude/skills/` directory. The harness is read-only
  against your install — its only output is files inside this repo.

## Requirements

- Python 3.9+ (stdlib only — no `pip install`).
- Claude Code installed (for step 4; step 4 is optional).

## Platform support

| Platform | Status | Notes |
|---|---|---|
| **macOS** | ✅ Tested | Confirmed working against `~/.claude/projects/*.jsonl` and `~/.claude/skills/`. |
| **Linux** | ✅ Tested | Same paths as macOS; tested on Ubuntu. |
| **Windows (native)** | ⚠️ Not tested | Should work in principle — the scripts use `pathlib` and `~` expansion, no shell-specific calls — but the JSONL transcript layout under `%USERPROFILE%\.claude\projects\` has not been verified. The `orchestrate.sh` driver is bash; you'll need WSL or to port it to PowerShell. |
| **Windows (WSL)** | ⚠️ Likely works | Same as Linux if Claude Code is installed in WSL. If Claude Code is installed on the Windows host instead, point `--projects-dir` at `/mnt/c/Users/<you>/.claude/projects` (untested). |

If you confirm or fix Windows support, PRs welcome.

## Customizing

Three knobs you'll likely want to tweak:

1. **Synthesis prompt.** Edit the heredoc in `scripts/orchestrate.sh`
   to match how you want recommendations framed.
2. **Noise filter.** `scripts/extract-prompts.py` has a
   `NOISE_PREFIXES` tuple that drops slash-command echoes, system
   reminders, and compaction summaries. Add more if your transcripts
   include other system-generated content.
3. **Model budget.** `--max-budget-usd N` flag on `orchestrate.sh`
   (default `$3.00`).

## License

MIT — see [LICENSE](LICENSE).

## Related

- [Claude Code skills documentation](https://docs.claude.com/claude-code)
- `superpowers:writing-skills` — official TDD-style skill authoring
  guide (a skill, not a doc — invoke via `/superpowers:writing-skills`
  in Claude Code).
