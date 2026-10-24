#!/usr/bin/env python3
"""Translate missing UI strings with the Claude API and add them to js/i18n/<lang>.js.

Needs the anthropic package and ANTHROPIC_API_KEY. Used by the weekly sync
workflow after a new release of the original project is merged.

Usage:
    python tools/i18n/translate.py de            # translate everything missing
    python tools/i18n/translate.py de --dry-run  # only list what would be sent
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract  # noqa: E402
import locale_file  # noqa: E402

MODEL = "claude-opus-5-5"
BATCH = 150

SYSTEM = """You translate the web interface of Tautulli, a monitoring and statistics tool for
Plex Media Server (streams, watch history, users, libraries, notifications, newsletters), from
English into German for Switzerland.

Rules:
- Swiss spelling: never use "ß", always "ss" (e.g. "schliessen", "Grösse").
- Address the user informally with "du" (lowercase).
- Keep placeholders such as {0}, {1} exactly; you may reorder them. A placeholder that only
  adds an English plural "s" may be dropped (write "Element(e)" or rephrase instead).
- Many strings are fragments of a sentence around a link or a bold word. Translate the fragment
  so the sentence still reads naturally, keep leading/trailing punctuation.
- Keep product and service names unchanged (Tautulli, Plex, Plex Media Server, Plex Pass, Plex
  Web, Discord, Telegram, Pushover, Webhook, MQTT, IMDb, TMDb, TVmaze, MusicBrainz, ...).
- Use these terms consistently: library = Mediathek, history = Verlauf, user = Benutzer,
  stream = Stream, play/plays = Wiedergabe/Wiedergaben, direct play = Direktwiedergabe,
  direct stream = Direkt-Stream, transcode = Transkodierung, notification agent =
  Benachrichtigungsdienst, newsletter agent = Newsletter-Dienst, trigger = Auslöser,
  recently added = «Neu hinzugefügt», settings = Einstellungen, logs = Protokolle,
  movie = Film, TV show = Serie, season = Staffel, episode = Folge, artist = Interpret,
  track = Titel, collection = Sammlung, watched = gesehen, home = Start.
- Short labels stay short; keep capitalisation style (ALL CAPS stays all caps).
- Quote UI names with «» when the English text refers to a button or page by name.
- If a string is code, a CSS class, a URL or otherwise not human text, return it unchanged."""

SCHEMA = {
    "type": "object",
    "properties": {
        "translations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"source": {"type": "string"}, "target": {"type": "string"}},
                "required": ["source", "target"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["translations"],
    "additionalProperties": False,
}


def translate_batch(client, items: list[str]) -> dict[str, str]:
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
        system=SYSTEM,
        messages=[{"role": "user", "content": "Translate these strings. Return every source string exactly as given.\n\n"
                   + json.dumps(items, ensure_ascii=False, indent=1)}],
    )
    if response.stop_reason in ("refusal", "max_tokens"):
        raise RuntimeError(f"translation stopped: {response.stop_reason}")
    text = next(b.text for b in response.content if b.type == "text")
    wanted = set(items)
    out = {}
    for row in json.loads(text).get("translations", []):
        src, dst = row.get("source", ""), row.get("target", "")
        if src in wanted and dst and not locale_file.problems(src, dst):
            out[src] = dst
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("lang")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    have = locale_file.load(args.lang)
    ignore = extract.load_ignore()
    missing = [s for s in extract.collect() if s not in have and s not in ignore]
    print(f"{len(missing)} strings missing for {args.lang}")
    if not missing or args.dry_run:
        print("\n".join(missing))
        return 0

    import anthropic

    client = anthropic.Anthropic()
    added = 0
    for i in range(0, len(missing), BATCH):
        batch = missing[i:i + BATCH]
        result = translate_batch(client, batch)
        have.update(result)
        added += len(result)
        locale_file.save(args.lang, have)
        print(f"batch {i // BATCH + 1}: {len(result)}/{len(batch)} translated")
    print(f"{added} strings added")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
