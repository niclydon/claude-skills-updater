# process

The four-step "what skills should I add?" workflow.

## Why this exists

Without a catalog and a prompt corpus, every recommendation pass forces
a full rediscovery: walk every JSONL transcript, summarize the existing
skill set, eyeball patterns, write recommendations. Doing it once is
useful. Doing it monthly is tedious. This repo turns the workflow into
four small commands.

## When to run

- After installing a new plugin (skill set just changed).
- After a heavy month of new project work (prompt patterns shift).
- Periodic hygiene pass (monthly or quarterly).
- Whenever you catch yourself rephrasing the same multi-step ask three
  times in a week.

## Step 1 — Refresh the catalog

```
python3 scripts/inventory.py
```

Walks `~/.claude/skills/<name>/SKILL.md` (user-level personal skills)
and `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/skills/<name>/SKILL.md`
(plugin-bundled skills). Writes:

- `catalogs/<today>.json` — dated snapshot.
- `catalogs/latest.json` — copy of the same.

Each entry: `{name, source, description, path}`. `source` is `user` or
`plugin:<plugin-name>`. User-level skills win on name collision.

The script is stdlib-only and does not import any installed skill — it
just parses the YAML frontmatter via two regexes (`name:` and
`description:`).

## Step 2 — See what changed

```
python3 scripts/catalog-diff.py
```

Compares `latest.json` against the most recent prior snapshot whose
contents differ. Reports added / removed / description-changed /
source-changed skills.

Use cases:

- A plugin update silently retired a skill you were relying on.
- Two skills now have overlapping descriptions; one should be retired.
- You added a personal skill but forgot to commit it elsewhere.

## Step 3 — Mine the prompt corpus

```
python3 scripts/extract-prompts.py
```

Walks every JSONL under `~/.claude/projects/`. For each, emits one TSV
row per real user message:

```
<cwd>\t<timestamp>\t<prompt-text-truncated-to-500-chars>
```

A "real" user message is:

- `.type == "user"`
- `.isSidechain == false`
- `.message.content` is a string (not an array of `tool_result` blocks)
- and is NOT a system-generated echo

System-generated echoes that get filtered:

- `<local-command-…>` — slash command stdout
- `<command-name>` / `<command-message>` / `<command-args>` blocks
- `<task-notification>` — background task events
- `<system-reminder>` — harness reminders
- "You are summarizing a …" — compaction prompts
- "This session is being …" — handoff prompts
- "Apply maximum non-destructive compression" — known summary preambles

Add to `NOISE_PREFIXES` in `scripts/extract-prompts.py` if your
transcripts include other system-generated text.

Output goes to `prompts/<today>.tsv` and `prompts/latest.tsv`. The
`prompts/` directory is gitignored — the corpus is your raw
conversation history and may contain personal data.

## Step 4 — Run the synthesis

```
./scripts/orchestrate.sh --label <something-short>
```

Calls `claude -p` with both inputs and a fixed instruction prompt
asking for ranked candidate skills that:

- Recur (5+ asks across sessions, or a clearly repeatable workflow)
- Have a non-obvious procedure (otherwise the LLM could wing it)
- Benefit from project-specific knowledge (paths, conventions,
  gotchas)
- Are NOT covered by an existing skill in `catalogs/latest.json`

Output: `recommendations/<today>-<label>.md`. Format: 8–15 ranked
candidates, each with name, trigger, what-it-does, why-it's-a-gap, and
leverage notes. Plus a "skipped (already covered or too thin)"
section.

Flags:

- `--dry-run` — print the prompt instead of calling claude.
- `--refresh` — re-run steps 1+3 first.
- `--max-budget-usd N` — cap spend (default `$3.00`).
- `--label <name>` — suffix for the output file.

## After a pass

In order of likelihood:

1. **Pick the top 3–6 candidates** that match how you actually work.
   Don't build all 12; pick the highest-leverage ones.
2. **Author each chosen skill.** Use `superpowers:writing-skills` for
   a TDD-style workflow (baseline-fail → write skill → confirm
   compliance → refactor).
3. **Re-run `inventory.py`** so the new skills appear in the next
   catalog and won't be re-recommended.

## What this process doesn't do

- It doesn't author skills. The recommendations file is a triage
  queue, not generated `SKILL.md` files.
- It doesn't remove or rename existing skills. The diff surfaces
  drift; you decide what to do.
- It doesn't deduplicate against plugin updates automatically. If a
  plugin ships a skill that overlaps with one of yours, the diff will
  show the addition and you decide.

## Convention recap

- Stdlib-only Python; same-day re-runs idempotent.
- `catalogs/` committed; `prompts/` gitignored;
  `recommendations/` committed (review for personal data first if
  you'll publish).
- Recommendations are dated + labeled so multiple passes per day
  don't collide.
- Never write into `~/.claude/skills/` from these scripts.
