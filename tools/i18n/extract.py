#!/usr/bin/env python3
"""Collect user-visible English UI strings from the Tautulli web interface.

Scans the Mako templates and the JavaScript under data/interfaces/default and
the UI texts that the Python code sends to the browser (setting labels,
descriptions, messages), keeps strings that look like human text and writes
them as a sorted JSON list.  Dynamic parts (Mako ${...}, JavaScript string
concatenation, DataTables _START_ etc.) become {0}, {1}, ... so the runtime
can match them as patterns.

Usage:
    python tools/i18n/extract.py                 # write tools/i18n/strings.json
    python tools/i18n/extract.py --missing de    # list strings missing in js/i18n/de.js
"""
from __future__ import annotations

import argparse
import ast
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import locale_file  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tools" / "i18n" / "strings.json"
IGNORE = ROOT / "tools" / "i18n" / "ignore.json"
UI = ROOT / "data" / "interfaces" / "default"

TEMPLATES = ["*.html"]
JS_FILES = ["js/script.js", "js/ajaxNotifications.js", "js/dataTables.bootstrap.pagination.js",
            "js/tables/*.js", "js/graphs/*.js"]
PY_FILES = ["plexpy/*.py"]
# Pages that are not part of the web interface
SKIP_TEMPLATES = {"newsletter_preview.html"}
# dict keys in the Python code whose values are shown in the web interface
PY_KEYS = {"label", "description", "message", "stat_title", "category", "placeholder", "help_text",
           "select_all_label"}
PY_KEYS_PER_FILE = {"graphs.py": {"name"}, "common.py": {"example"}}
# (name, kind) tuples of the scheduler list in common.py
PY_SCHEDULER_KINDS = {"scheduled", "websocket"}

ATTRS = ("title", "placeholder", "aria-label", "alt", "data-original-title", "data-content", "data-title", "label")

WORD = re.compile(r"[A-Za-z]{2,}")
# a tag may contain ">" only inside quoted attribute values; text may contain a bare ">"
HTML_TAG = re.compile(r"<[A-Za-z/!][^<>\"']*(?:(?:\"[^\"]*\"|'[^']*')[^<>\"']*)*>")
BUTTON_VALUE = re.compile(r"<input\b[^>]*\btype=[\"'](?:button|submit|reset)[\"'][^>]*>", re.I)
HTML_ATTR = re.compile(r"\b(?:%s)\s*=\s*(\"[^\"]*\"|'[^']*')" % "|".join(re.escape(a) for a in ATTRS))
PH = "\x00"


# ---- JavaScript -----------------------------------------------------------

def _js_literals(src: str):
    """Yield (start, end, value) for every JS string literal in src."""
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c == "/" and i + 1 < n and src[i + 1] == "/":
            j = src.find("\n", i)
            i = n if j < 0 else j
            continue
        if c == "/" and i + 1 < n and src[i + 1] == "*":
            j = src.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        if c in "'\"`":
            start = i
            i += 1
            buf = []
            while i < n:
                ch = src[i]
                if ch == "\\" and i + 1 < n:
                    buf.append(src[i:i + 2])
                    i += 2
                    continue
                if c == "`" and ch == "$" and i + 1 < n and src[i + 1] == "{":
                    end = _expr_end(src, i + 2)
                    buf.append(PH)
                    i = end + 1
                    continue
                if ch == c or (ch == "\n" and c != "`"):
                    break
                buf.append(ch)
                i += 1
            yield start, i + 1, "".join(buf)
            i += 1
            continue
        i += 1


def _expr_end(src: str, i: int) -> int:
    """Index of the "}" closing a ${...} expression that starts at i."""
    n, depth = len(src), 1
    while i < n:
        ch = src[i]
        if ch in "'\"":
            i += 1
            while i < n and src[i] != ch and src[i] != "\n":
                i += 2 if src[i] == "\\" else 1
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return n


# a simple expression between two "+" of a string concatenation
_CONCAT_GAP = re.compile(r"^\s*\+\s*[\w$.\[\]()'\"!?:|&, -]*?\s*\+\s*$", re.S)
_CONCAT_TAIL = re.compile(r"^\s*\+\s*[\w$.\[\]()]+(?:\([^()'\"]*\))?\s*(?=[;,)\n}])")
_CONCAT_HEAD = re.compile(r"[\w$.\]]+(?:\([^()'\"]*\))?\s*\+\s*$")
_SKIP_PREFIX = re.compile(
    r"(?:console\.\w+|\$|jQuery|querySelector(?:All)?|getElementById|addClass|removeClass|toggleClass|hasClass|"
    r"attr|prop|data|find|closest|is|on|off|trigger|url|ajax|getJSON|css|getItem|setItem|removeItem|"
    r"split|indexOf|replace|startsWith|endsWith|includes|format)\(\s*$|"
    r"(?:url|type|dataType|className|data|targets|width|order)\"?\s*:\s*$|==+\s*$|!=+\s*$|case\s+$")


def _unescape_js(s: str) -> str:
    def esc(m):
        e = m.group(1)
        if e[0] in "ux" and len(e) > 1:
            return chr(int(e[1:], 16))
        return {"n": "\n", "t": "\t", "r": ""}.get(e, e)
    return re.sub(r"\\(u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|.)", esc, s)


def scan_js_source(src: str, found: set[str]) -> None:
    lits = [lit for lit in _js_literals(src) if not _SKIP_PREFIX.search(src[max(0, lit[0] - 40):lit[0]])]
    # join "a" + expr + "b" into "a{x}b"
    groups, cur = [], []
    for lit in lits:
        if cur and _CONCAT_GAP.match(src[cur[-1][1]:lit[0]]) and "\n\n" not in src[cur[-1][1]:lit[0]]:
            cur.append(lit)
        else:
            if cur:
                groups.append(cur)
            cur = [lit]
    if cur:
        groups.append(cur)
    for g in groups:
        parts = [_unescape_js(v) for _, _, v in g]
        for p in parts:
            _add_js(p, found)
        joined = PH.join(parts)
        if _CONCAT_HEAD.search(src[max(0, g[0][0] - 60):g[0][0]]):
            joined = PH + joined
        if _CONCAT_TAIL.match(src[g[-1][1]:g[-1][1] + 80]):
            joined += PH
        if len(g) > 1 or joined != parts[0]:
            _add_js(joined, found)


def _add_js(val: str, found: set[str]) -> None:
    # DataTables placeholders
    val = re.sub(r"_(?:START|END|TOTAL|MAX|PAGE|PAGES)_", PH, val)
    if "_MENU_" in val:
        for part in val.split("_MENU_"):
            _add_js(part, found)
        return
    if "<" in val and ">" in val:
        from_markup(">" + val + "<", found)
    else:
        add(val, found)


# ---- markup and text ------------------------------------------------------

def normalize(s: str) -> str:
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def looks_human(s: str, markup: bool = False) -> bool:
    """markup: s is the text of an HTML element, so it cannot be a class list or code."""
    if not s or len(s) > 600 or not WORD.search(s):
        return False
    if markup and s.startswith(". "):
        s = s[2:]  # the rest of a sentence after a link: "<a>FAQ</a>. Your data ..."
    if s.startswith(("http://", "https://", "/", "data:", "#", ".", "--", "[", "]", ")", "<", "{", "&")):
        return False
    if '="' in s or "='" in s or "\\" in s:
        return False
    if re.search(r"[{};]\s*$", s) and ":" in s:  # css
        return False
    if re.fullmatch(r"[\w.\-/:#\[\]=\"'()>*,+~^$|@!%]+", s):
        # single token: keep only capitalised words such as "Save" or "IP"
        return bool(re.fullmatch(r"(?:[A-Z][a-z]+(?:[A-Z][a-z]+)?|[A-Z]{2,})[.!?:…]?", s))
    if re.search(r"\bfunction\s*\(|\breturn\s+[\w$(]|\b(?:var|const|let)\s+[\w$]+\s*=|=>|\btypeof\b|\bundefined\b"
                 r"|[=;]\s*$|\w\(\)", s):
        return False
    if re.search(r"(?:^|\s)[.#][a-z][\w-]*(?:\s|$)", s) and not re.search(r"[A-Z][a-z]+ [a-z]+", s):
        return False  # selector list
    letters = sum(ch.isalpha() for ch in s)
    if letters < len(s) * 0.45:
        return False
    if not markup and re.fullmatch(r"[a-z0-9_\-]+(?: [a-z0-9_\-]+)*", s) and not re.search(
            r"\b(?:the|to|of|and|or|is|no|not|a|an|for|in|on|with|your|this|from|by|at|all)\b", s):
        return False  # class lists, keywords
    return True


def from_markup(s: str, found: set[str]) -> None:
    for text in HTML_TAG.split(s):
        add(text.strip("<>"), found, markup=True)
    for m in HTML_ATTR.finditer(s):
        add(m.group(1)[1:-1], found)
    for m in BUTTON_VALUE.finditer(s):
        v = re.search(r"\bvalue=(\"[^\"]*\"|'[^']*')", m.group(0))
        if v:
            add(v.group(1)[1:-1], found)


def add(raw: str, found: set[str], markup: bool = False) -> None:
    text = normalize(raw)
    k = 0

    def sub(_m):
        nonlocal k
        k += 1
        return "{%d}" % (k - 1)

    text = re.sub(PH, sub, text)
    if not text or re.fullmatch(r"[\W\d]*(?:\{\d+\}[\W\d]*)*", text):
        return
    if looks_human(normalize(re.sub(r"\{\d+\}", " ", text)), markup):
        found.add(text)
        # a placeholder at the start or end is often markup of its own ("Label ${help_icon}"),
        # so the DOM may show the text without it
        bare = re.sub(r"^(?:\{\d+\}\s*)+|(?:\s*\{\d+\})+$", "", text)
        if bare != text and "{" not in bare and looks_human(bare, markup):
            found.add(bare)


# ---- Mako templates -------------------------------------------------------

def _mako_expr_end(src: str, i: int) -> int:
    depth, n = 1, len(src)
    while i < n:
        ch = src[i]
        if ch in "'\"":
            q = ch
            i += 1
            while i < n and src[i] != q:
                i += 2 if src[i] == "\\" else 1
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return n


def strip_mako(src: str) -> str:
    src = re.sub(r"(?s)<%doc>.*?</%doc>", "", src)
    src = re.sub(r"(?s)<%(?![a-z/]).*?%>", "", src)        # <% code %> and <%! code %>
    src = re.sub(r"(?m)^\s*##.*$", "", src)                # comments
    src = re.sub(r"(?m)^\s*%(?!>).*$", "", src)            # % if / % for / % endif
    out, i = [], 0
    while True:
        j = src.find("${", i)
        if j < 0:
            out.append(src[i:])
            break
        out.append(src[i:j])
        out.append(PH)
        i = _mako_expr_end(src, j + 2) + 1
    return "".join(out)


def scan_template(path: Path, found: set[str]) -> None:
    src = strip_mako(path.read_text(encoding="utf-8", errors="replace"))
    for script in re.findall(r"(?s)<script\b[^>]*>(.*?)</script>", src):
        scan_js_source(script, found)
    src = re.sub(r"(?s)<script\b.*?</script>|<style\b.*?</style>", "", src)
    from_markup(src, found)


# ---- Python ---------------------------------------------------------------

def _py_text(node) -> str | None:
    """Plain or formatted string of an AST node, dynamic parts as placeholders."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(v.value if isinstance(v, ast.Constant) else PH for v in node.values)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "format":
        base = _py_text(node.func.value)
        return re.sub(r"\{[^{}]*\}", PH, base) if base is not None else None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        base = _py_text(node.left)
        return re.sub(r"%[sdif]", PH, base) if base is not None else None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _py_text(node.left), _py_text(node.right)
        if left is None and right is None:
            return None
        return (left if left is not None else PH) + (right if right is not None else PH)
    return None


def scan_py(path: Path, found: set[str]) -> None:
    keys = PY_KEYS | PY_KEYS_PER_FILE.get(path.name, set())
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", getattr(node.func, "attr", "")) == "serve_template":
            # page titles: serve_template(template_name="...", title="History")
            for kw in node.keywords:
                if kw.arg == "title":
                    _add_py(_py_text(kw.value), found)
        if (isinstance(node, ast.Tuple) and len(node.elts) == 2
                and all(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in node.elts)
                and node.elts[1].value in PY_SCHEDULER_KINDS):
            _add_py(node.elts[0].value, found)
        if isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and k.value in keys:
                    _add_py(_py_text(v), found)
                elif isinstance(k, ast.Constant) and k.value == "select_options" and isinstance(v, ast.Dict):
                    for ov in v.values:
                        _add_py(_py_text(ov), found)


def _add_py(text: str | None, found: set[str]) -> None:
    if not text:
        return
    if "<" in text and ">" in text:
        from_markup(">" + text + "<", found)
    else:
        add(text, found)


# ---- main -----------------------------------------------------------------

def collect() -> list[str]:
    found: set[str] = set()
    for pattern in TEMPLATES:
        for p in sorted(UI.glob(pattern)):
            if p.name not in SKIP_TEMPLATES:
                scan_template(p, found)
    for pattern in JS_FILES:
        for p in sorted(UI.glob(pattern)):
            scan_js_source(p.read_text(encoding="utf-8", errors="replace"), found)
    for pattern in PY_FILES:
        for p in sorted(ROOT.glob(pattern)):
            scan_py(p, found)
    return sorted(found, key=lambda s: (s.lower(), s))


def load_ignore() -> set[str]:
    return set(json.loads(IGNORE.read_text(encoding="utf-8"))) if IGNORE.exists() else set()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--missing", metavar="LANG", help="print strings missing in js/i18n/LANG.js")
    ap.add_argument("--json", action="store_true", help="with --missing: print JSON list")
    args = ap.parse_args()
    strings = collect()
    if args.missing:
        sys.stdout.reconfigure(encoding="utf-8")
        have = locale_file.load(args.missing)
        ignore = load_ignore()
        missing = [s for s in strings if s not in have and s not in ignore]
        if args.json:
            print(json.dumps(missing, ensure_ascii=False, indent=1))
        else:
            print("\n".join(missing))
        print(f"{len(missing)} missing of {len(strings)}", file=sys.stderr)
        return 0
    OUT.write_text(json.dumps(strings, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(strings)} strings -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
