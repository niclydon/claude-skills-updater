#!/usr/bin/env python3
"""Diff two skill-catalog snapshots from catalogs/.

Default: latest.json vs the most recent prior dated snapshot whose
contents differ.

Usage:
    python3 scripts/catalog-diff.py
    python3 scripts/catalog-diff.py catalogs/2026-04-15.json catalogs/latest.json
    python3 scripts/catalog-diff.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def pick_default_pair(catalogs_dir: Path) -> tuple[Path, Path] | None:
    latest = catalogs_dir / "latest.json"
    if not latest.exists():
        return None
    dated = sorted(p for p in catalogs_dir.glob("*.json") if p.name != "latest.json")
    if not dated:
        return None
    latest_text = latest.read_text()
    prior = None
    for p in reversed(dated):
        if p.read_text() != latest_text:
            prior = p
            break
    if prior is None:
        prior = dated[-2] if len(dated) >= 2 else dated[-1]
    return prior, latest


def index(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {s["name"]: s for s in snapshot.get("skills", [])}


def diff_snapshots(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    a_idx = index(a)
    b_idx = index(b)
    added = sorted(set(b_idx) - set(a_idx))
    removed = sorted(set(a_idx) - set(b_idx))
    changed: list[dict[str, str]] = []
    for name in sorted(set(a_idx) & set(b_idx)):
        if a_idx[name].get("description") != b_idx[name].get("description"):
            changed.append({
                "name": name,
                "old": a_idx[name].get("description", ""),
                "new": b_idx[name].get("description", ""),
            })
        elif a_idx[name].get("source") != b_idx[name].get("source"):
            changed.append({
                "name": name,
                "old_source": a_idx[name].get("source", ""),
                "new_source": b_idx[name].get("source", ""),
            })
    return {
        "a_generated_at": a.get("generated_at"),
        "b_generated_at": b.get("generated_at"),
        "added": [{"name": n, **b_idx[n]} for n in added],
        "removed": [{"name": n, **a_idx[n]} for n in removed],
        "changed": changed,
        "totals": {
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
        },
    }


def render(diff: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"a: {diff.get('a_generated_at')}")
    lines.append(f"b: {diff.get('b_generated_at')}")
    t = diff["totals"]
    lines.append(f"totals: +{t['added']} -{t['removed']} ~{t['changed']}")
    lines.append("")

    if diff["added"]:
        lines.append("== added ==")
        for s in diff["added"]:
            lines.append(f"  + {s['name']} ({s.get('source','?')})")
            if s.get("description"):
                lines.append(f"      {s['description']}")
        lines.append("")
    if diff["removed"]:
        lines.append("== removed ==")
        for s in diff["removed"]:
            lines.append(f"  - {s['name']} ({s.get('source','?')})")
        lines.append("")
    if diff["changed"]:
        lines.append("== changed ==")
        for c in diff["changed"]:
            lines.append(f"  ~ {c['name']}")
            if "old" in c:
                lines.append(f"      old: {c['old']}")
                lines.append(f"      new: {c['new']}")
            else:
                lines.append(f"      source: {c['old_source']} -> {c['new_source']}")
        lines.append("")
    if not (diff["added"] or diff["removed"] or diff["changed"]):
        lines.append("(no changes)")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("a", nargs="?", help="older snapshot")
    ap.add_argument("b", nargs="?", help="newer snapshot")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    here = Path(__file__).resolve().parents[1]
    catalogs = here / "catalogs"

    if args.a and args.b:
        a_path, b_path = Path(args.a), Path(args.b)
    else:
        pair = pick_default_pair(catalogs)
        if pair is None:
            print(
                "need at least two snapshots in catalogs/ "
                "(or pass them explicitly)",
                file=sys.stderr,
            )
            return 1
        a_path, b_path = pair

    a = load(a_path)
    b = load(b_path)
    diff = diff_snapshots(a, b)
    if args.json:
        print(json.dumps(diff, indent=2))
    else:
        print(f"diffing {a_path.name} -> {b_path.name}")
        print()
        print(render(diff))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
