#!/usr/bin/env python3
"""Extract real user-typed prompts from ~/.claude/projects/*.jsonl.

Walks every JSONL transcript in `--projects-dir` (default
`~/.claude/projects`) and emits one TSV line per real user message:

    cwd<TAB>timestamp<TAB>prompt_text   (truncated to 500 chars)

A "real" user message is:
  - .type == "user"
  - .isSidechain == false
  - .message.content is a string (not an array of tool_result blocks)
  - and is NOT a system-generated echo (slash-command stdout, task
    notifications, compaction summaries, system reminders, etc.)

Output:
    prompts/<YYYY-MM-DD>.tsv
    prompts/latest.tsv

Stdlib-only. Same-day re-runs overwrite in place. The prompts/ dir is
gitignored — the corpus contains personal data.

Usage:
    python3 scripts/extract-prompts.py
    python3 scripts/extract-prompts.py --projects-dir ~/.claude/projects
    python3 scripts/extract-prompts.py --no-write   # print to stdout
    python3 scripts/extract-prompts.py --keep-noise # don't filter system echoes
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Iterable

NOISE_PREFIXES = (
    "<local-command-",
    "<command-name>",
    "<command-message>",
    "<command-args>",
    "<task-notification>",
    "<system-reminder>",
    "You are summarizing a ",
    "This session is being ",
    "You are a memory ",
    "Apply maximum non-destructive compression",
    "Caveat: The messages below",
)


def is_noise(text: str) -> bool:
    head = text.lstrip()[:80]
    return any(head.startswith(p) for p in NOISE_PREFIXES)


def extract_one(path: Path) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    try:
        with path.open("r", errors="ignore") as fh:
            for line in fh:
                if '"type":"user"' not in line and '"type": "user"' not in line:
                    continue
                try:
                    obj = json.loads(line)
                except (json.JSONDecodeError, ValueError):
                    continue
                if obj.get("type") != "user":
                    continue
                if obj.get("isSidechain"):
                    continue
                msg = obj.get("message") or {}
                content = msg.get("content")
                if not isinstance(content, str):
                    continue  # tool_result arrays etc.
                cwd = obj.get("cwd") or "?"
                ts = obj.get("timestamp") or "?"
                rows.append((cwd, ts, content))
    except OSError:
        return rows
    return rows


def extract_all(
    projects_dir: Path, keep_noise: bool, max_chars: int
) -> Iterable[tuple[str, str, str]]:
    files = list(projects_dir.rglob("*.jsonl"))
    if not files:
        return []
    out: list[tuple[str, str, str]] = []
    with ThreadPoolExecutor(max_workers=min(16, (os.cpu_count() or 4) * 2)) as pool:
        for batch in pool.map(extract_one, files):
            out.extend(batch)
    if not keep_noise:
        out = [r for r in out if not is_noise(r[2])]
    # Truncate and squash newlines so each row stays one TSV line.
    cleaned: list[tuple[str, str, str]] = []
    for cwd, ts, text in out:
        flat = re.sub(r"\s+", " ", text).strip()
        if not flat:
            continue
        if len(flat) > max_chars:
            flat = flat[:max_chars]
        cleaned.append((cwd, ts, flat))
    cleaned.sort(key=lambda r: r[1])
    return cleaned


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects-dir", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--keep-noise", action="store_true")
    ap.add_argument("--max-chars", type=int, default=500)
    args = ap.parse_args()

    projects_dir = Path(args.projects_dir).expanduser()
    here = Path(__file__).resolve().parents[1]
    out_dir = Path(args.out_dir) if args.out_dir else here / "prompts"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = list(extract_all(projects_dir, args.keep_noise, args.max_chars))
    today = dt.date.today().isoformat()
    print(
        f"extracted {len(rows)} prompts from {projects_dir}",
        file=sys.stderr,
    )

    def lines() -> Iterable[str]:
        for cwd, ts, text in rows:
            yield f"{cwd}\t{ts}\t{text}\n"

    if args.no_write:
        for line in lines():
            sys.stdout.write(line)
        return 0

    dated = out_dir / f"{today}.tsv"
    latest = out_dir / "latest.tsv"
    with dated.open("w") as fh:
        for line in lines():
            fh.write(line)
    with latest.open("w") as fh:
        for line in lines():
            fh.write(line)
    print(f"wrote {dated}")
    print(f"wrote {latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
