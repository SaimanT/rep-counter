"""Generates every page, manifest, the sitemap and the offline file list.

Run from anywhere:  python site/_build/build.py
Folders starting with "_" are not published by GitHub Pages.

English is the main version (site root), Russian lives under /ru/. Texts are in
content_en.py and content_ru.py; pages with the same "id" are translations of each other.
"""
import hashlib
import json
import re
from datetime import date
from html import escape
from pathlib import Path

import content_en
import content_ru

BASE = "https://saimant.github.io/rep-counter/"
SITE = Path(__file__).resolve().parent.parent
VERIFY = """<meta name="google-site-verification" content="_M29k6wRQseVUyZRi4jtbQvlDl-PdW_5S8K-UQpaX8g">
<meta name="yandex-verification" content="9246cb77e3bfb61f">"""
LANGS = [(content_en.UI, content_en.PAGES), (content_ru.UI, content_ru.PAGES)]
MAIN_LANG = "en"


def page_path(ui, page):
    return ui["prefix"] + (page["slug"] + "/" if page["slug"] else "")


# Every page with its language, path and translations — also used by the tests
PAGES = []
for _ui, _pages in LANGS:
    for _p in _pages:
        PAGES.append({**_p, "lang": _ui["lang"], "ui": _ui, "path": page_path(_ui, _p)})
for _p in PAGES:
    _p["alts"] = {q["lang"]: q["path"] for q in PAGES if q["id"] == _p["id"]}

# The first version had Russian pages at the root: keep those addresses working
OLD_PATHS = {p["slug"] + "/": p["path"] for p in PAGES if p["lang"] == "ru" and p["slug"]}

TEMPLATE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="theme-color" content="#101214">
<link rel="canonical" href="{url}">
{alternates}
{verify}
<link rel="manifest" href="{home}manifest.webmanifest">
<link rel="icon" href="{root}icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{root}icon-192.png">
<link rel="stylesheet" href="{root}app.css?v={css_v}">
<meta property="og:type" content="website">
<meta property="og:locale" content="{og_locale}">
{og_alt_locales}
<meta property="og:url" content="{url}">
<meta property="og:title" content="{h1}{og_title_suffix}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{base}og/{lang}-{id}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">
{jsonld}
</script>
</head>
<body data-store="{store}" data-default-plan="{plan}" data-root="{root}">
<section id="app" aria-label="{app_label}">
  <div class="top">
    <h1>{h1}</h1>
    <div class="tools">
      <button id="install" hidden>{install}</button>
      <button id="sound" class="icon" aria-label="{sound}" aria-pressed="true">🔊</button>
      <button id="fullscreen" class="icon" aria-label="{fullscreen}">⛶</button>
    </div>
  </div>
  <div class="plan">
    <label for="plan">{plan_label}</label>
    <input id="plan" type="number" min="1" inputmode="numeric" value="{plan}">
    <div class="presets">
      {presets}
    </div>
  </div>
  <div class="count" id="count" aria-live="polite">0</div>
  <div class="info">
    {info}
  </div>
  <div class="progress"><div id="bar"></div></div>
  <div class="sets" id="sets"></div>
  <div class="controls">
    <button id="minus" aria-label="{minus}">−1</button>
    <button id="finish">{finish}</button>
    <button id="reset">{reset}</button>
  </div>
  <div class="help">
    <span class="keys">{keys}<br></span>
    {tap} · <a href="#about">{howto_link}</a>
  </div>
</section>

<main id="about">{body}
  <h2>{faq_title}</h2>
{faq}
{more}
</main>
<footer><a href="{home}">{home_name}</a> · {footer_tail} · {switch}</footer>
<script src="{root}app.js?v={js_v}"></script>
</body>
</html>
"""

REDIRECT = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={target}">
<script>location.replace('{target}' + location.hash)</script>
</head>
<body><a href="{target}">{title}</a></body>
</html>
"""


def rel_root(path):
    return "../" * path.count("/")


def links_html(page, root, skip=None):
    items = "\n".join(
        f'    <li><a href="{root}{q["path"]}">{escape(q["h1"])}</a></li>'
        for q in PAGES if q["lang"] == page["lang"] and q["slug"] and q["id"] != skip
    )
    return f'  <ul class="links">\n{items}\n  </ul>'


def jsonld(page, url):
    ui = page["ui"]
    graph = [
        {
            "@type": "WebApplication",
            "name": page["h1"],
            "url": url,
            "applicationCategory": "HealthApplication",
            "operatingSystem": ui["os"],
            "inLanguage": ui["lang"],
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": ui["currency"]},
            "description": page["description"],
        },
        {
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in page["faq"]
            ],
        },
    ]
    if page["slug"]:
        graph.append({
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": ui["home_name"], "item": BASE + ui["prefix"]},
                {"@type": "ListItem", "position": 2, "name": page["h1"], "item": url},
            ],
        })
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)


def version(name):
    """Short content hash, so browsers fetch a fresh copy after every change."""
    return hashlib.sha1((SITE / name).read_bytes()).hexdigest()[:8]


def render(page):
    ui = page["ui"]
    root = rel_root(page["path"])
    home = root + ui["prefix"] or "./"
    url = BASE + page["path"]
    alternates = "\n".join(
        [f'<link rel="alternate" hreflang="{lang}" href="{BASE}{path}">' for lang, path in page["alts"].items()]
        + [f'<link rel="alternate" hreflang="x-default" href="{BASE}{page["alts"][MAIN_LANG]}">']
    )
    other = [(lang, path) for lang, path in page["alts"].items() if lang != page["lang"]]
    og_alt_locales = "\n".join(
        f'<meta property="og:locale:alternate" content="{next(u for u, _ in LANGS if u["lang"] == lang)["og_locale"]}">'
        for lang, _ in other)
    # ui["switch"] is the other language's own name ("Русский" on English pages)
    switch = " · ".join(f'<a href="{root}{path}" hreflang="{lang}" lang="{lang}">{ui["switch"]}</a>'
                        for lang, path in other)
    presets = "".join(f'<button data-plan="{n}">{n}</button>' for n in page["presets"])
    faq = "\n".join(f"  <h3>{escape(q)}</h3>\n  <p>{escape(a)}</p>" for q, a in page["faq"])
    more = "" if not page["slug"] else f'  <h2>{ui["more_title"]}</h2>\n' + links_html(page, root, skip=page["id"])
    lang_module = content_en if page["lang"] == "en" else content_ru
    how_to = lang_module.CONTROLS.replace("{home}", home) if page["slug"] else lang_module.HOW_TO
    body = page["body"].replace("{how_to}", how_to).replace("{links}", links_html(page, root))
    return TEMPLATE.format(
        lang=page["lang"], title=escape(page["title"]), description=escape(page["description"]), url=url,
        alternates=alternates, verify=VERIFY, root=root, home=home, base=BASE, id=page["id"],
        css_v=version("app.css"), js_v=version("app.js"), og_locale=ui["og_locale"], og_alt_locales=og_alt_locales,
        og_title_suffix=ui["og_title_suffix"], h1=escape(page["h1"]), jsonld=jsonld(page, url),
        store=page["store"], plan=page["plan"], presets=presets, info=ui["info"].format(plan=page["plan"]),
        app_label=ui["app_label"], install=ui["install"], sound=ui["sound"], fullscreen=ui["fullscreen"],
        plan_label=ui["plan"], minus=ui["minus"], finish=ui["finish"], reset=ui["reset"], keys=ui["keys"],
        tap=ui["tap"], howto_link=ui["howto_link"], body=body, faq_title=ui["faq_title"], faq=faq, more=more,
        home_name=ui["home_name"], footer_tail=ui["footer_tail"], switch=switch,
    )


def write(rel, text):
    out = SITE / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8", newline="\n")


def manifest(ui):
    root = rel_root(ui["prefix"])
    home = next(p for p in PAGES if p["lang"] == ui["lang"] and not p["slug"])
    return json.dumps({
        "name": ui["home_name"],
        "short_name": ui["home_name"],
        "description": home["description"],
        "lang": ui["lang"],
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "background_color": "#101214",
        "theme_color": "#101214",
        "icons": [
            {"src": f"{root}icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": f"{root}icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": f"{root}icon.svg", "sizes": "any", "type": "image/svg+xml"},
        ],
    }, ensure_ascii=False, indent=2) + "\n"


def sitemap():
    today = date.today().isoformat()
    entries = []
    for p in PAGES:
        alts = "".join(
            f'\n    <xhtml:link rel="alternate" hreflang="{lang}" href="{BASE}{path}"/>'
            for lang, path in [*p["alts"].items(), ("x-default", p["alts"][MAIN_LANG])])
        entries.append(f"  <url>\n    <loc>{BASE}{p['path']}</loc>\n    <lastmod>{today}</lastmod>{alts}\n  </url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(entries) + "\n</urlset>\n")


def offline_files():
    """Keep the service worker's precache list in sync with the pages."""
    files = (["./", "index.html", "app.css", "app.js", "icon.svg", "icon-192.png", "icon-512.png"]
             + [u["prefix"] + "manifest.webmanifest" for u, _ in LANGS]
             + [p["path"] for p in PAGES if p["path"]])
    sw = (SITE / "sw.js").read_text(encoding="utf-8")
    listing = "const FILES = [\n" + "".join(f"  '{f}',\n" for f in files) + "];"
    sw = re.sub(r"const FILES = \[.*?\];", listing, sw, flags=re.S)
    sw = re.sub(r"const CACHE = '[^']*';",
                f"const CACHE = 'rep-counter-{hashlib.sha1(listing.encode()).hexdigest()[:8]}';", sw)
    write("sw.js", sw)


def main():
    for p in PAGES:
        write(p["path"] + "index.html", render(p))
    for old, new in OLD_PATHS.items():
        page = next(p for p in PAGES if p["path"] == new)
        write(old + "index.html", REDIRECT.format(title=escape(page["title"]), url=BASE + new, target="../" + new))
    for ui, _ in LANGS:
        write(ui["prefix"] + "manifest.webmanifest", manifest(ui))
    write("sitemap.xml", sitemap())
    offline_files()
    print(f"Built {len(PAGES)} pages in {len(LANGS)} languages, {len(OLD_PATHS)} redirects")


if __name__ == "__main__":
    main()
