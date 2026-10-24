"""Tests for the additions of this fork (fork_addons.py, tools/i18n)."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "lib"))
sys.path.insert(0, os.path.join(ROOT, "tools", "i18n"))

import fork_addons  # noqa: E402
import extract  # noqa: E402
import locale_file  # noqa: E402


def test_language_from_cookie_wins(monkeypatch):
    monkeypatch.setenv("TAUTULLI_UI_LANG", "de")
    assert fork_addons.pick_language("a=1; tautulli_lang=en", "de-CH") == "en"


def test_language_from_environment_then_browser(monkeypatch):
    monkeypatch.setenv("TAUTULLI_UI_LANG", "de")
    assert fork_addons.pick_language("", "en-US") == "de"
    monkeypatch.delenv("TAUTULLI_UI_LANG")
    assert fork_addons.pick_language("", "fr-CH, de;q=0.8") == "de"
    assert fork_addons.pick_language("", "fr-CH") == "en"


def test_inject_adds_scripts_once(monkeypatch):
    monkeypatch.setattr(fork_addons.plexpy, "HTTP_ROOT", "/tautulli/", raising=False)
    html = '<!doctype html>\n<html lang="en">\n<head>\n<title>x</title></head><body></body></html>'
    out = fork_addons.inject(html, "de")
    assert '<html lang="de" data-tautulli-lang="de">' in out
    assert 'src="/tautulli/js/i18n/de.js' in out
    assert out.index("js/i18n/i18n.js") < out.index("<title>")
    assert fork_addons.inject(out, "de") == out


def test_inject_leaves_fragments_alone():
    fragment = '<div class="dashboard-activity">Movie</div>'
    assert fork_addons.inject(fragment, "de") == fragment


def test_every_ui_string_is_translated_or_ignored():
    have = locale_file.load("de")
    ignore = extract.load_ignore()
    missing = [s for s in extract.collect() if s not in have and s not in ignore]
    assert missing == []


def test_translations_keep_placeholders_and_swiss_spelling():
    for key, value in locale_file.load("de").items():
        assert locale_file.problems(key, value) == [], (key, value)


def test_dictionary_is_valid_json():
    src = locale_file.path_for("de").read_text(encoding="utf-8")
    data = json.loads(src[src.index("{", src.index("=")): src.rindex("}") + 1])
    assert data["lang"] == "de" and data["strings"] and data["locale"]["highcharts"]["months"][2] == "März"
