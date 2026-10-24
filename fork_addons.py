# -*- coding: utf-8 -*-

#  This file is part of the German Tautulli fork (brunoz78/Tautulli).
#
#  Tautulli is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

"""Entry point for everything this fork adds.

Tautulli.py calls install() once after the config is loaded, so merges from
the original project touch a single line.

- UI language: every rendered page gets the runtime translator
  (js/i18n/i18n.js) and the dictionary of the chosen language. The language
  comes from the tautulli_lang cookie, otherwise from TAUTULLI_UI_LANG,
  otherwise from the browser's Accept-Language header.
- Updates: the built-in updater looks for new versions in this fork instead
  of the original repository.
"""

import os
import re

import cherrypy

import plexpy
from plexpy import logger, webserve

SUPPORTED_LANGS = ('en', 'de')
FORK_USER = 'brunoz78'
FORK_REPO = 'Tautulli'

_I18N_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'interfaces', 'default', 'js', 'i18n')
_COOKIE_RE = re.compile(r'(?:^|;\s*)tautulli_lang=([a-z]{2})')
_HEAD_RE = re.compile(r'<head(?:\s[^>]*)?>', re.IGNORECASE)
_HTML_LANG_RE = re.compile(r'<html([^>]*?)\slang="[a-zA-Z-]*"', re.IGNORECASE)
# Pages that are not part of the web interface (newsletters are e-mails)
_SKIP_TEMPLATES = ('newsletter_preview.html',)


def pick_language(cookie_header, accept_language):
    m = _COOKIE_RE.search(cookie_header or '')
    if m and m.group(1) in SUPPORTED_LANGS:
        return m.group(1)
    env = (os.getenv('TAUTULLI_UI_LANG') or '').strip().lower()[:2]
    if env in SUPPORTED_LANGS:
        return env
    for part in (accept_language or '').split(','):
        code = part.split(';')[0].strip().lower()[:2]
        if code in SUPPORTED_LANGS:
            return code
    return 'en'


def _version(name):
    try:
        return str(int(os.stat(os.path.join(_I18N_DIR, name)).st_mtime))
    except OSError:
        return '0'


def _tags(lang):
    root = plexpy.HTTP_ROOT or '/'
    tags = []
    if lang != 'en' and os.path.isfile(os.path.join(_I18N_DIR, lang + '.js')):
        tags.append('<script src="%sjs/i18n/%s.js?v=%s"></script>' % (root, lang, _version(lang + '.js')))
    tags.append('<script src="%sjs/i18n/i18n.js?v=%s"></script>' % (root, _version('i18n.js')))
    return ''.join(tags)


def inject(html, lang):
    """Add the translator scripts right after <head> and set <html lang>."""
    if not isinstance(html, str) or 'js/i18n/i18n.js' in html:
        return html
    m = _HEAD_RE.search(html)
    if not m:
        return html
    html = html[:m.end()] + _tags(lang) + html[m.end():]
    return _HTML_LANG_RE.sub(lambda h: '<html%s lang="%s" data-tautulli-lang="%s"' % (h.group(1), lang, lang),
                             html, count=1)


def _wrap_serve_template(original):
    def serve_template(template_name, **kwargs):
        html = original(template_name, **kwargs)
        if template_name in _SKIP_TEMPLATES:
            return html
        try:
            headers = cherrypy.request.headers
            lang = pick_language(headers.get('Cookie', ''), headers.get('Accept-Language', ''))
        except Exception:
            lang = 'en'
        return inject(html, lang)

    serve_template.__wrapped__ = original
    return serve_template


def _use_fork_updates():
    # Only replace the original's default so a manual entry in config.ini wins.
    if plexpy.CONFIG.GIT_USER.lower() == 'tautulli' and plexpy.CONFIG.GIT_REPO.lower() == 'tautulli':
        plexpy.CONFIG.GIT_USER = FORK_USER
        plexpy.CONFIG.GIT_REPO = FORK_REPO
        logger.info('Fork :: Updates are checked against %s/%s', FORK_USER, FORK_REPO)


def install():
    if not hasattr(webserve.serve_template, '__wrapped__'):
        webserve.serve_template = _wrap_serve_template(webserve.serve_template)
    _use_fork_updates()
