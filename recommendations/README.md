# recommendations

One markdown file per recommendation pass. File naming:

```
recommendations/<YYYY-MM-DD>-<label>.md
```

The `label` is a short tag for the pass — useful when more than one
runs per day (e.g. `2026-05-04-initial`, `2026-05-04-after-broadside`).

## What goes in here

Output of `./scripts/orchestrate.sh`. Each file is a ranked list of
candidate new skills, with:

- Name + tagline
- Trigger phrasing
- What it does (workflow sketch)
- Why it's a gap (evidence from the prompt corpus)
- Leverage estimate

Plus a "Skipped (already covered or too thin)" section at the bottom.

## What doesn't go in here

- The SKILL.md files themselves. Those land at
  `~/.claude/skills/<name>/SKILL.md` after a deliberate authoring
  pass (see `superpowers:writing-skills`).
- Raw prompt excerpts containing PII. The corpus stays at
  `prompts/` (gitignored). Recommendations cite *patterns*, not
  literal user content.

## Lifecycle of a candidate

```
recommendation file  ->  user picks top N  ->  author SKILL.md  ->  next inventory.py picks it up
```

A recommendation that has been built moves out of the candidate
pool the next time `inventory.py` runs (because it's now in
`catalogs/latest.json` and the synthesis prompt drops duplicates).

If a candidate has been recommended multiple passes in a row and
*not* built, it's a signal: either it's not actually useful (retire
the idea), or it's blocked on something else (note the blocker).
