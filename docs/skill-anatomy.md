# skill anatomy

Reference for what a Claude Code SKILL.md looks like and what the
fields mean. Used by `inventory.py` for parsing and by recommendation
passes to suggest new skills in a consistent shape.

## File layout

User-level personal skills:

```
~/.claude/skills/
  <skill-name>/
    SKILL.md            # required
    examples/           # optional
    references/         # optional
    *.md                # optional supporting docs
```

Plugin-bundled skills mirror this under
`~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/skills/<name>/SKILL.md`.

## SKILL.md frontmatter contract

Minimum fields:

```yaml
---
name: <skill-name>
description: <one sentence on when to trigger this skill>
---
```

Optional fields seen in the wild:

```yaml
allowed-tools:           # restrict tool access while the skill runs
  - "Read"
  - "Write"
  - "stitch*:*"
```

The `description` field is what the harness shows to the model when
deciding whether to activate the skill. Write it as a *trigger*, not a
summary. Examples:

- Good: `Use when the user asks "what's next here?", "how's it
  looking?", or any session-start status briefing.`
- Bad: `Helps with project management.`

## Body structure

After the frontmatter, prose. Common sections that work well:

- **When to use** — concrete trigger phrases the user actually says.
- **Required reading first** — paths the skill must consult before
  acting.
- **Procedure** — numbered steps. Order matters when the skill
  encodes a sequence (e.g. model-lifecycle).
- **Pitfalls** — gotchas the model would otherwise rediscover. Include
  the *why*, not just the *what*.

Skills can be:

- **Rigid** (e.g. TDD, debugging) — follow exactly; do not adapt away
  the discipline.
- **Flexible** (patterns) — adapt to context.

State which type the skill is in the body if it's not obvious.

## Naming

`<noun-or-verb>-<scope>` works well:

- `narrative-docs-update`, `model-lifecycle`, `nexus-orphan-audit` —
  verb + scope.
- `secrets-vault`, `nexus-db-query` — noun + scope when the noun is
  the thing being operated on.

Avoid:

- Generic single-word names (`docs`, `query`, `deploy`) — too easy to
  collide with plugins.
- Marketing-style names (`turbo-deploy`, `easy-query`) — descriptions
  should sell the trigger; names should describe the thing.

## Authoring workflow

Use `superpowers:writing-skills`. It enforces a TDD-style flow:

1. Pick a pressure scenario where the agent currently fails without
   the skill (the RED step).
2. Write the SKILL.md (the GREEN step).
3. Confirm the agent now follows the skill on the same scenario.
4. Refactor to close loopholes.

Don't author skills inline in this repo — they live at
`~/.claude/skills/`. This repo only suggests them.

## Reading a SKILL.md programmatically

`inventory.py` parses the frontmatter with two regexes:

- `^---\s*\n(.*?)\n---\s*\n` to grab the YAML block.
- `^name:\s*(.+?)\s*$` and `^description:\s*(.+?)\s*$` inside it.

That's intentional — skills with complex YAML (lists, nested objects)
still parse for the two fields we care about, and we don't take a
PyYAML dependency.

If you want to surface other fields (e.g. `allowed-tools`), add a
parser branch in `inventory.py` rather than swapping in a YAML lib.
