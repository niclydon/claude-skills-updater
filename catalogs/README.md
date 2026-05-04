# catalogs

Snapshots of every skill installed under `~/.claude/skills/` and
`~/.claude/plugins/cache/*/`. One file per refresh:

```
catalogs/
  YYYY-MM-DD.json
  latest.json       # copy of the most recent dated snapshot
```

These files are committed by design — the history *is* the point. A
diff between snapshots tells you what plugins added or retired skills,
which user-level skills you've authored over time, and where
descriptions drifted.

Generate one with:

```
python3 scripts/inventory.py
```

This directory ships empty in the public repo. Your first
`inventory.py` run creates `catalogs/<today>.json` from your local
install.

## Schema

Each snapshot:

```jsonc
{
  "generated_at": "2026-01-15T...",
  "claude_home": "/Users/you/.claude",
  "counts": { "user": 6, "plugin": 47, "total": 53 },
  "skills": [
    {
      "name": "narrative-docs-update",
      "source": "user",
      "description": "Use when the user says 'update docs'...",
      "path": "/Users/you/.claude/skills/narrative-docs-update/SKILL.md"
    },
    {
      "name": "writing-plans",
      "source": "plugin:superpowers",
      "description": "Use when you have a spec...",
      "path": "/Users/you/.claude/plugins/cache/.../skills/writing-plans/SKILL.md"
    }
  ]
}
```

The schema is intentionally minimal. Add fields by editing
`scripts/inventory.py` — keep it stdlib-only.
