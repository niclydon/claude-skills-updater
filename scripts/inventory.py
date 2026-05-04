#!/usr/bin/env python3
"""Build a catalog snapshot of every installed Claude Code skill.

Walks two roots:
    ~/.claude/skills/<name>/SKILL.md          — user-level
    ~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/skills/<name>/SKILL.md
                                              — plugin-bundled

Outputs:
    catalogs/<YYYY-MM-DD>.json
    catalogs/latest.json

Stdlib-only. Safe to run repeatedly; same-day re-runs overwrite in place.

Usage:
    python3 scripts/inventory.py
    python3 scripts/inventory.py --claude-home ~/.claude
    python3 scripts/inventory.py --no-write   # print summary only
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
NAME_RE = re.compile(r"^name:\s*(.+?)\s*$", re.M)
DESC_RE = re.compile(r"^description:\s*(.+?)\s*$", re.M)


def parse_skill(path: Path) -> dict[str, Any] | None:
    try:
        text = path.read_text(errors="ignore")
    except OSError:
        return None
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    fm = m.group(1)
    name_m = NAME_RE.search(fm)
    desc_m = DESC_RE.search(fm)
    if not name_m:
        return None
    return {
        "name": name_m.group(1).strip(),
        "description": (desc_m.group(1).strip() if desc_m else ""),
        "path": str(path),
    }


def collect_user_skills(claude_home: Path) -> list[dict[str, Any]]:
    base = claude_home / "skills"
    if not base.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue
        skill_md = child / "SKILL.md"
        if not skill_md.is_file():
            continue
        info = parse_skill(skill_md)
        if info is None:
            continue
        info["source"] = "user"
        out.append(info)
    return out


def collect_plugin_skills(claude_home: Path) -> list[dict[str, Any]]:
    cache = claude_home / "plugins" / "cache"
    if not cache.is_dir():
        return []
    out: list[dict[str, Any]] = []
    # cache/<marketplace>/<plugin>/<version>/skills/<name>/SKILL.md
    for skill_md in cache.rglob("SKILL.md"):
        # Only accept files under a .../skills/<name>/SKILL.md path.
        parts = skill_md.parts
        if "skills" not in parts:
            continue
        info = parse_skill(skill_md)
        if info is None:
            continue
        # Identify plugin from the path: .../cache/<marketplace>/<plugin>/<version>/skills/...
        try:
            cache_idx = parts.index("cache")
            plugin = parts[cache_idx + 2]
        except (ValueError, IndexError):
            plugin = "unknown"
        info["source"] = f"plugin:{plugin}"
        out.append(info)
    return out


def build_snapshot(claude_home: Path) -> dict[str, Any]:
    user = collect_user_skills(claude_home)
    plugin = collect_plugin_skills(claude_home)
    # Dedup: user-level wins on name collision; among plugin entries, keep
    # the first encountered (rglob order is fs-dependent — note the caveat).
    seen: set[str] = set()
    skills: list[dict[str, Any]] = []
    for entry in user + plugin:
        key = entry["name"]
        if key in seen:
            continue
        seen.add(key)
        skills.append(entry)
    skills.sort(key=lambda s: (s["source"] != "user", s["name"]))
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "claude_home": str(claude_home),
        "counts": {
            "user": sum(1 for s in skills if s["source"] == "user"),
            "plugin": sum(1 for s in skills if s["source"].startswith("plugin:")),
            "total": len(skills),
        },
        "skills": skills,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--claude-home", default=os.path.expanduser("~/.claude"))
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    claude_home = Path(args.claude_home).expanduser()
    here = Path(__file__).resolve().parents[1]
    out_dir = Path(args.out_dir) if args.out_dir else here / "catalogs"
    out_dir.mkdir(parents=True, exist_ok=True)

    snapshot = build_snapshot(claude_home)
    today = dt.date.today().isoformat()
    print(
        f"snapshot {today}: {snapshot['counts']['total']} skills "
        f"({snapshot['counts']['user']} user, {snapshot['counts']['plugin']} plugin)",
        file=sys.stderr,
    )

    if args.no_write:
        print(json.dumps(snapshot, indent=2))
        return 0

    dated = out_dir / f"{today}.json"
    latest = out_dir / "latest.json"
    dated.write_text(json.dumps(snapshot, indent=2))
    latest.write_text(json.dumps(snapshot, indent=2))
    print(f"wrote {dated}")
    print(f"wrote {latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
