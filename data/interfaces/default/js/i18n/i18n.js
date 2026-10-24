/* js/i18n/i18n.js */
/* Tautulli - runtime UI translation (fork addition) */
/* Translates English UI text in the DOM using window.TAUTULLI_I18N_DICT. Loaded
   synchronously at the start of <head> so text is replaced before the first paint. */
(() => {
  "use strict";
  if (window.tautulliI18n) return;

  const COOKIE = "tautulli_lang";
  const LANGS = { en: "English", de: "Deutsch" };
  const ATTRS = ["title", "placeholder", "aria-label", "alt", "data-original-title", "data-content", "data-title", "label"];
  const SKIP = new Set(["SCRIPT", "STYLE", "TEXTAREA", "CODE", "PRE", "NOSCRIPT", "math"]);
  // Elements whose text is user data (names, titles, paths, log lines), never UI text
  const DATA_SELECTOR = [
    "[data-no-i18n]", "[translate='no']", ".ace_editor", "#log-modal-content", "#tautulli_log_table td",
    "#tautulli_api_log_table td", "#plex_websocket_log_table td", "#plex_log_table td",
    ".highcharts-credits", ".dashboard-activity-metadata-title", ".dashboard-activity-metadata-subtitle",
    ".dashboard-recent-media-metacontainer h3", ".dashboard-stats-info-title .sub-value",
    ".dashboard-stats-info-item .sub-value", ".item-children-instance-text-wrapper h3",
    ".summary-content-title", ".summary-content-summary", ".summary-poster-face-container",
  ].join(",");

  const readCookie = () => {
    const m = document.cookie.match(/(?:^|;\s*)tautulli_lang=([a-z]{2})/);
    return m ? m[1] : "";
  };
  const lang = (document.documentElement.getAttribute("data-tautulli-lang") || readCookie() || "en").toLowerCase();
  const dict = (window.TAUTULLI_I18N_DICT && window.TAUTULLI_I18N_DICT.lang === lang) ? window.TAUTULLI_I18N_DICT : null;
  const strings = (dict && dict.strings) || {};
  const active = !!dict && lang !== "en";

  // ---- lookup -----------------------------------------------------------
  const norm = (s) => s.replace(/\s+/g, " ").trim();
  const exact = new Map();
  const byWord = new Map();
  const reEsc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  // Separators in meta lines such as "Movie - 2026 - 2h"
  const SEP = / [-·•|–] /;

  const values = new Set();
  for (const [k, v] of Object.entries(strings)) {
    if (!v) continue;
    values.add(norm(v));
    if (/\{\d+\}/.test(k)) {
      // A pattern made of two or more placeholders around a single word is too
      // loose: it would also rewrite user data.
      const literalWords = (k.replace(/\{\d+\}/g, " ").match(/[A-Za-z]{2,}/g) || []).length;
      if ((k.match(/\{\d+\}/g) || []).length >= 2 && literalWords < 2) continue;
      const order = [];
      const src = k.split(/(\{\d+\})/).map((part) => {
        const m = part.match(/^\{(\d+)\}$/);
        if (m) { order.push(+m[1]); return "([\\s\\S]*?)"; }
        return reEsc(part);
      }).join("");
      const words = (k.replace(/\{\d+\}/g, " ").match(/[A-Za-z]{3,}/g) || []);
      const entry = { re: new RegExp("^" + src + "$"), out: v, order, len: k.replace(/\{\d+\}/g, "").length, sep: SEP.test(k) };
      const key = (words.sort((a, b) => b.length - a.length)[0] || "").toLowerCase();
      if (!byWord.has(key)) byWord.set(key, []);
      byWord.get(key).push(entry);
    } else {
      exact.set(k, v);
    }
  }

  // Rules for text built from numbers: [regex, replacement] for the whole text, or
  // [regex, replacement, "seq"] for a run of matches such as "2 days 3 hrs 5 mins".
  // In the replacement "{t2}" stands for capture group 2 looked up in the strings.
  const rules = ((dict && dict.rules) || []).map(([re, out, mode]) => (mode === "seq"
    ? { test: new RegExp("^(?:" + re + ")(?: (?:" + re + "))*$"), re: new RegExp(re, "g"), out }
    : { test: new RegExp("^" + re + "$"), re: new RegExp("^" + re + "$"), out }));
  const applyRule = (r, key) => key.replace(r.re, (...m) => r.out.replace(/\{t(\d)\}|\$(\d)/g, (_, t, d) => {
    const g = m[+(t || d)] || "";
    return t && exact.has(g) ? exact.get(g) : g;
  }));

  const cache = new Map();
  const missing = new Set();
  const debug = (() => { try { return localStorage.getItem("tautulli_i18n_debug") === "1"; } catch (e) { return false; } })();

  function translate(text, depth = 0) {
    const key = norm(text);
    if (!key || !/[A-Za-z]/.test(key)) return null;
    if (cache.has(key)) return cache.get(key);
    let out = exact.has(key) ? exact.get(key) : null;
    if (out == null) {
      for (const r of rules) {
        if (r.test.test(key)) { out = applyRule(r, key); break; }
      }
    }
    if (out == null && !values.has(key)) {
      // collect candidates from every word, most specific pattern first
      const cands = new Set(byWord.get("") || []);
      for (const w of new Set((key.match(/[A-Za-z]{3,}/g) || []).map((x) => x.toLowerCase()))) {
        for (const p of byWord.get(w) || []) cands.add(p);
      }
      for (const p of [...cands].sort((a, b) => b.len - a.len)) {
        const m = key.match(p.re);
        if (!m) continue;
        const vals = p.order.map((_, i) => m[i + 1]);
        if (!p.sep && vals.some((v) => SEP.test(` ${v || ""} `))) continue;
        out = p.out.replace(/\{(\d+)\}/g, (_, n) => {
          const v = vals[p.order.indexOf(+n)] || "";
          const t = depth < 2 ? translate(v, depth + 1) : exact.get(norm(v));
          return t == null ? v : t;
        });
        break;
      }
    }
    if (out == null && depth < 2 && / [-·•|–]$/.test(key)) {
      // a separator left at the end, e.g. "Tautulli - Settings |" without a server name
      const t = translate(key.slice(0, -2), depth + 1);
      if (t != null) out = t + key.slice(-2);
    }
    if (out == null && depth < 2 && SEP.test(key)) {
      // translate each part of a separated line on its own
      const parts = key.split(/( [-·•|–] )/);
      let changed = false;
      const tr = parts.map((part, i) => {
        if (i % 2) return part;
        const t = translate(part, depth + 1);
        if (t != null && t !== part) changed = true;
        return t == null ? part : t;
      });
      if (changed) out = tr.join("");
    }
    if (out != null) values.add(norm(out));
    else if (debug && active && key.length > 1 && !values.has(key) && /[A-Z ]/.test(key)) missing.add(key);
    if (cache.size > 20000) cache.clear();
    cache.set(key, out);
    return out;
  }

  function withSpace(orig, tr) {
    const lead = orig.match(/^\s*/)[0];
    const trail = orig.match(/\s*$/)[0];
    return lead + tr + trail;
  }

  // ---- DOM walking ------------------------------------------------------
  const done = new WeakMap(); // node -> translated value we wrote

  function skipped(el) {
    for (let n = el; n && n.nodeType === 1; n = n.parentNode) {
      if (SKIP.has(n.nodeName)) return true;
      if (n.isContentEditable) return true;
    }
    return !!(el.closest && el.closest(DATA_SELECTOR));
  }

  function doText(node) {
    const v = node.data;
    if (done.get(node) === v) return;
    if (!v || v.length > 2000 || !/[A-Za-z]/.test(v)) return;
    const parent = node.parentNode;
    if (!parent || parent.nodeType !== 1 || skipped(parent)) return;
    const tr = translate(v);
    if (tr != null) {
      const nv = withSpace(v, tr);
      done.set(node, nv);
      if (nv !== v) node.data = nv;
    }
  }

  function doAttrs(el) {
    if (skipped(el)) return;
    for (const a of ATTRS) {
      const v = el.getAttribute(a);
      if (!v || /[<>]/.test(v)) continue;
      const tr = translate(v);
      if (tr != null && tr !== v) el.setAttribute(a, tr);
    }
    if (el.nodeName === "INPUT" && /^(button|submit|reset)$/i.test(el.type) && el.value) {
      const tr = translate(el.value);
      if (tr != null && tr !== el.value) el.value = tr;
    }
  }

  function walk(root) {
    if (root.nodeType === 3) return doText(root);
    if (root.nodeType !== 1 && root.nodeType !== 9 && root.nodeType !== 11) return;
    if (root.nodeType === 1) {
      if (SKIP.has(root.nodeName)) return;
      doAttrs(root);
    }
    const tw = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, {
      acceptNode(n) {
        if (n.nodeType === 1 && SKIP.has(n.nodeName)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    });
    let n;
    while ((n = tw.nextNode())) {
      if (n.nodeType === 3) doText(n);
      else doAttrs(n);
    }
  }

  // ---- dialogs ----------------------------------------------------------
  function wrapDialogs() {
    for (const name of ["alert", "confirm", "prompt"]) {
      const orig = window[name];
      if (typeof orig !== "function" || orig.__tautulliI18n) continue;
      const wrapped = function (msg, ...rest) {
        if (typeof msg === "string") {
          const tr = msg.split("\n").map((line) => {
            if (!line.trim()) return line;
            const t = translate(line);
            return t == null ? line : t;
          }).join("\n");
          return orig.call(window, tr, ...rest);
        }
        return orig.call(window, msg, ...rest);
      };
      wrapped.__tautulliI18n = true;
      window[name] = wrapped;
    }
  }

  // ---- libraries: dates and charts --------------------------------------
  // moment and Highcharts are loaded later at the end of <body>; set their
  // language the moment the library defines its global.
  function onGlobal(name, setup) {
    if (window[name]) { setup(window[name]); return; }
    let value;
    try {
      Object.defineProperty(window, name, {
        configurable: true,
        get: () => value,
        set: (v) => {
          value = v;
          Object.defineProperty(window, name, { configurable: true, writable: true, value: v });
          try { setup(v); } catch (e) { /* keep the page working */ }
        },
      });
    } catch (e) { /* property not configurable */ }
  }

  function setupLibraries() {
    const loc = dict && dict.locale;
    if (!loc) return;
    onGlobal("moment", (m) => {
      if (!m || !m.locale) return;
      m.locale(lang);
      // moment-duration-format calls updateLocale("en"), which also switches the global locale
      const update = m.updateLocale;
      if (typeof update === "function") {
        m.updateLocale = function (...args) {
          const current = m.locale();
          const result = update.apply(this, args);
          m.locale(current);
          return result;
        };
      }
    });
    onGlobal("Highcharts", (h) => {
      if (!h || !h.setOptions || !loc.highcharts) return;
      h.setOptions({ lang: loc.highcharts });
    });
  }

  // ---- language switch --------------------------------------------------
  function setLang(next) {
    const l = LANGS[next] ? next : "en";
    document.cookie = `${COOKIE}=${l}; path=/; max-age=31536000; SameSite=Lax`;
    location.reload();
  }

  function mountSwitch() {
    const tab = document.getElementById("tabs-general");
    if (!tab || document.getElementById("tautulli_ui_language")) return;
    const head = tab.querySelector(".padded-header");
    if (!head) return;
    const group = document.createElement("div");
    group.className = "form-group";
    // no name attribute: the value is a browser cookie, not part of the saved settings
    group.innerHTML =
      '<label for="tautulli_ui_language">Interface Language</label>' +
      '<div class="row"><div class="col-md-4">' +
      '<select class="form-control" id="tautulli_ui_language"></select>' +
      "</div></div>" +
      '<p class="help-block">Language of the Tautulli web interface in this browser.</p>';
    const sel = group.querySelector("select");
    for (const [code, label] of Object.entries(LANGS)) {
      const o = document.createElement("option");
      o.value = code;
      o.textContent = label;
      o.setAttribute("data-no-i18n", "");
      if (code === lang) o.selected = true;
      sel.appendChild(o);
    }
    sel.addEventListener("change", (e) => { e.stopPropagation(); setLang(sel.value); });
    head.parentNode.insertBefore(group, head.nextSibling);
    if (active) walk(group);
  }

  // ---- start ------------------------------------------------------------
  const api = {
    lang,
    languages: Object.assign({}, LANGS),
    t: (s) => { if (!active) return s; const t = translate(s); return t == null ? s : t; },
    setLang,
    missing: () => [...missing].sort(),
    retranslate: () => active && walk(document.documentElement),
  };
  window.tautulliI18n = api;

  if (active) {
    document.documentElement.lang = lang;
    setupLibraries();
    wrapDialogs();
    const queue = new Set();
    const mo = new MutationObserver((records) => {
      for (const r of records) {
        if (r.type === "childList") r.addedNodes.forEach((n) => queue.add(n));
        else if (r.type === "characterData") queue.add(r.target);
        else if (r.type === "attributes") queue.add(r.target);
      }
      // translate in the same microtask turn to avoid an English flash
      for (const n of queue) if (n.isConnected) walk(n);
      queue.clear();
    });
    mo.observe(document.documentElement, {
      childList: true, subtree: true, characterData: true,
      attributes: true, attributeFilter: ATTRS.concat(["value"]),
    });
    walk(document.documentElement);
    document.addEventListener("DOMContentLoaded", () => { wrapDialogs(); walk(document.documentElement); }, { once: true });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mountSwitch, { once: true });
  else mountSwitch();
})();
