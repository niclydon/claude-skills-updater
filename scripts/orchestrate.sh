#!/usr/bin/env bash
# Drive `claude -p` to produce a fresh skills recommendation pass.
#
# Inputs (will refresh if missing):
#   catalogs/latest.json    — installed skills (run scripts/inventory.py)
#   prompts/latest.tsv      — extracted user prompts (run scripts/extract-prompts.py)
#
# Output:
#   recommendations/<YYYY-MM-DD>-<label>.md
#
# Modes:
#   default            headless `claude -p` one-shot
#   --dry-run          print prompt only, do not call claude
#
# Flags:
#   --label <name>     suffix for the recommendation file (default: pass)
#   --max-budget-usd N forwarded to `claude -p` (default: 3.00)
#   --refresh          force-rebuild catalog and prompts before running
#
# Env:
#   CLAUDE_BIN         (default: claude)

set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
CLAUDE_BIN="${CLAUDE_BIN:-claude}"

mode="headless"
label="pass"
max_budget="3.00"
refresh=0

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) mode="dry-run"; shift;;
    --label) label="$2"; shift 2;;
    --max-budget-usd) max_budget="$2"; shift 2;;
    --refresh) refresh=1; shift;;
    -h|--help) sed -n '2,25p' "$0"; exit 0;;
    *) echo "unknown flag: $1" >&2; exit 2;;
  esac
done

cd "$REPO"

if [ "$refresh" = "1" ] || [ ! -f catalogs/latest.json ]; then
  echo "[refresh] inventory.py"
  python3 scripts/inventory.py
fi
if [ "$refresh" = "1" ] || [ ! -f prompts/latest.tsv ]; then
  echo "[refresh] extract-prompts.py"
  python3 scripts/extract-prompts.py
fi

today="$(date +%Y-%m-%d)"
out="recommendations/${today}-${label}.md"

prompt=$(cat <<'EOF'
You are mining the user's Claude Code conversation history to recommend NEW
skills they should add. A "skill" is a reusable instruction pack at
~/.claude/skills/<name>/SKILL.md (or bundled in a plugin) that Claude loads
on-demand for a specific recurring task type.

## Inputs
- `catalogs/latest.json`       — every installed skill (user-level + plugin)
                                  with name + description + source. Do NOT
                                  recommend duplicates of anything in here.
- `prompts/latest.tsv`         — real user-typed prompts, one per line:
                                  cwd<TAB>timestamp<TAB>prompt (truncated to
                                  500 chars). Sample broadly; group by cwd
                                  to see which projects use which patterns.

## Your task
1. Read both inputs. Sample prompts widely; do not just read the top of the
   file.
2. Identify task patterns that:
   - Recur (5+ asks across sessions, or a clearly repeatable workflow)
   - Have a non-obvious procedure (otherwise the LLM could wing it)
   - Benefit from project-specific knowledge (paths, conventions, gotchas)
   - Are NOT covered by an existing skill in catalogs/latest.json
3. Cross-reference existing skills carefully — read their `description`
   fields to avoid near-duplicates.
4. Rank by frequency × leverage. Top of list = highest weekly value.

## Output format
Markdown. For each recommended skill:
```
### <skill-name> — short tagline
**Trigger:** when user says/does X
**What it does:** 2-3 lines on the workflow
**Why it's a gap:** evidence from the corpus (cite 2-4 example prompt
  patterns or counts)
**Leverage:** how often this comes up + why a skill beats winging it
```

Aim for 8-15 skills, ranked. Skip anything trivial or already covered. Be
concrete and grounded in what you actually saw in the prompts. If a
pattern is borderline, say so.

End with a short "## Skipped (already covered or too thin)" section.

Under 1500 words total.
EOF
)

case "$mode" in
  dry-run)
    echo "--- prompt that would be sent to claude ---"
    echo "$prompt"
    echo "--- end prompt ---"
    echo
    echo "would write: $out"
    ;;
  headless)
    if ! command -v "$CLAUDE_BIN" >/dev/null 2>&1; then
      echo "[error] $CLAUDE_BIN not found on PATH" >&2
      exit 1
    fi
    echo "[claude -p] generating recommendations (budget: \$$max_budget)"
    echo "[claude -p] writing to $out"
    mkdir -p recommendations
    printf '%s\n' "$prompt" | "$CLAUDE_BIN" \
      --add-dir "$REPO" \
      -p \
      --max-budget-usd "$max_budget" \
      > "$out"
    echo
    echo "wrote $out"
    ;;
esac
