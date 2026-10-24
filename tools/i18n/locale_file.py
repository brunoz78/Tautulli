"""Read and write data/interfaces/default/js/i18n/<lang>.js (a JSON object wrapped for the browser)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCALE_DIR = ROOT / "data" / "interfaces" / "default" / "js" / "i18n"
HEADER = "/* js/i18n/{lang}.js - {name} UI strings. Maintained with tools/i18n (extract.py, translate.py). */\n"
NAMES = {"de": "German"}
PLACEHOLDER = re.compile(r"\{\d+\}")


def path_for(lang: str) -> Path:
    return LOCALE_DIR / f"{lang}.js"


def _load_all(lang: str) -> dict:
    p = path_for(lang)
    if not p.exists():
        return {}
    src = p.read_text(encoding="utf-8")
    return json.loads(src[src.index("{", src.index("=")): src.rindex("}") + 1])


def load(lang: str) -> dict[str, str]:
    return dict(_load_all(lang).get("strings") or {})


def save(lang: str, strings: dict[str, str]) -> None:
    # "rules" (regular expressions for numbers) and "locale" (settings for moment
    # and Highcharts) are maintained by hand
    old = _load_all(lang)
    data = {"lang": lang, "locale": old.get("locale") or {}, "rules": old.get("rules") or [],
            "strings": dict(sorted(strings.items(), key=lambda kv: (kv[0].lower(), kv[0])))}
    text = HEADER.format(lang=lang, name=NAMES.get(lang, lang)) + "window.TAUTULLI_I18N_DICT = " \
        + json.dumps(data, ensure_ascii=False, indent=1) + ";\n"
    path_for(lang).write_text(text, encoding="utf-8", newline="\n")


def problems(key: str, value: str) -> list[str]:
    """Checks a translation against its source string."""
    out = []
    extra = set(PLACEHOLDER.findall(value)) - set(PLACEHOLDER.findall(key))
    if extra:
        out.append(f"unknown placeholder {sorted(extra)}")
    if "ß" in value:
        out.append("contains ß (Swiss spelling uses ss)")
    if not value.strip():
        out.append("empty")
    return out
