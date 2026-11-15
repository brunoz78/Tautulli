#!/usr/bin/env python3
"""Release notes from CHANGELOG.md and its translation CHANGELOG.<lang>.md.

Usage:
    python tools/i18n/changelog.py missing v2.19.1 de
        prints "yes" if CHANGELOG.de.md has no section for v2.19.1
    python tools/i18n/changelog.py notes v2.19.1 --since v2.18.2 [--lang de]
        prints the sections newer than v2.18.2 up to v2.19.1 as Markdown;
        with --lang the translation is used if it has every one of them
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECTION = re.compile(r"^##\s+(v\S+)")


def path_for(lang: str | None) -> Path:
    return ROOT / ("CHANGELOG.md" if not lang or lang == "en" else f"CHANGELOG.{lang}.md")


def sections(lang: str | None) -> list[tuple[str, str]]:
    """[(version, markdown)] in file order, newest first."""
    p = path_for(lang)
    if not p.exists():
        return []
    out: list[tuple[str, list[str]]] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        m = SECTION.match(line)
        if m:
            out.append((m.group(1), [line]))
        elif out:
            out[-1][1].append(line)
    return [(v, "\n".join(lines).strip()) for v, lines in out]


def between(secs: list[tuple[str, str]], upto: str, since: str | None) -> list[tuple[str, str]]:
    versions = [v for v, _ in secs]
    if upto not in versions:
        return []
    start = versions.index(upto)
    end = versions.index(since) if since in versions else start + 1
    return secs[start:max(end, start + 1)]


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("missing")
    m.add_argument("version")
    m.add_argument("lang")
    n = sub.add_parser("notes")
    n.add_argument("version")
    n.add_argument("--since")
    n.add_argument("--lang")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    if args.cmd == "missing":
        print("" if args.version in [v for v, _ in sections(args.lang)] else "yes")
        return 0

    english = between(sections(None), args.version, args.since)
    chosen = english
    if args.lang and args.lang != "en":
        translated = between(sections(args.lang), args.version, args.since)
        if translated and [v for v, _ in translated] == [v for v, _ in english]:
            chosen = translated
    # one heading level lower inside the release notes
    print("\n\n".join(re.sub(r"^## ", "### ", text) for _, text in chosen))
    return 0 if chosen else 1


if __name__ == "__main__":
    raise SystemExit(main())
