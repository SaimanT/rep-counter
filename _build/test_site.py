"""End-to-end checks for the site, run in a real browser (installed Edge via Playwright).

    python site/_build/test_site.py                          # live site
    python site/_build/test_site.py http://localhost:8765/site/

Needs: pip install playwright (no browser download — it uses the installed Edge).
"""
import json
import sys
import traceback
from xml.etree import ElementTree

from playwright.sync_api import sync_playwright

sys.path.insert(0, __import__("os").path.dirname(__file__))
from build import MAIN_LANG, OLD_PATHS, PAGES  # noqa: E402

BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://saimant.github.io/rep-counter/").rstrip("/") + "/"
LIVE = "https://saimant.github.io/rep-counter/"
SW_FILES = ["", "index.html", "app.css", "app.js", "manifest.webmanifest", "ru/manifest.webmanifest",
            "icon.svg", "icon-192.png", "icon-512.png"]
LOCALE = {"en": "en-US", "ru": "ru-RU"}

# Text the counter shows, per language
TXT = {
    "en": {"sets": "Sets: {n}", "total": "workout total: {n}", "intro": "Just one rep", "key": "press space",
           "intro_touch": "tap the screen", "first": "One done", "half": "You did one, 5 times",
           "done": "10 times just one", "set": "Set saved", "offer": "This page is also in English"},
    "ru": {"sets": "Подходы: {n}", "total": "всего за тренировку: {n}", "intro": "Только одно повторение",
           "key": "нажмите пробел", "intro_touch": "коснитесь экрана", "first": "Одно есть",
           "half": "вы сделали 5 раз по одному", "done": "10 раз по одному", "set": "Подход записан",
           "offer": "Эта страница есть на русском"},
}

results = []


def test(name):
    def wrap(fn):
        def run(*args):
            label = name.format(*args)
            try:
                fn(*args)
                results.append((True, label, ""))
                print(f"  ok    {label}")
            except Exception as e:  # noqa: BLE001
                msg = str(e) or traceback.format_exc(limit=1)
                results.append((False, label, msg))
                print(f"  FAIL  {label}\n        {msg}")
        return run
    return wrap


def url_of(page):
    return BASE + page["path"]


def home(lang):
    return next(p for p in PAGES if p["lang"] == lang and not p["slug"])


def eq(actual, expected, what):
    assert actual == expected, f"{what}: expected {expected!r}, got {actual!r}"


def state(p):
    return p.evaluate("""() => ({
        count: +document.getElementById('count').textContent,
        total: +document.getElementById('total').textContent,
        left: +document.getElementById('left').textContent,
        done: +document.getElementById('done').textContent,
        sets: document.getElementById('sets').textContent,
        finished: document.getElementById('app').classList.contains('finished'),
        plan: document.getElementById('plan').value,
        bar: document.getElementById('bar').style.width,
    })""")


def hint(p):
    return p.evaluate("""() => {
        const h = document.querySelector('.hint');
        return h && h.classList.contains('show') ? h.querySelector('span').textContent : '';
    }""")


# ---------------------------------------------------------------- SEO / static

@test("SEO: {0[lang]} {0[h1]}")
def seo(page, p):
    resp = p.goto(url_of(page))
    eq(resp.status, 200, "HTTP status")
    eq(p.title(), page["title"], "title")
    desc = p.get_attribute('meta[name="description"]', "content")
    eq(desc, page["description"], "description")
    assert 70 <= len(desc) <= 160, f"description length {len(desc)} outside 70–160 (cut off in search results)"
    assert len(p.title()) <= 60, f"title length {len(p.title())} > 60 (cut off in search results)"
    live_url = LIVE + page["path"]
    eq(p.get_attribute('link[rel="canonical"]', "href"), live_url, "canonical")
    eq(p.get_attribute('meta[property="og:url"]', "content"), live_url, "og:url")
    eq(p.get_attribute("html", "lang"), page["lang"], "html lang")
    eq(p.locator("h1").count(), 1, "number of h1")
    eq(p.inner_text("h1"), page["h1"], "h1")
    assert p.get_attribute('meta[name="google-site-verification"]', "content"), "no Google verification tag"
    assert p.get_attribute('meta[name="yandex-verification"]', "content"), "no Yandex verification tag"

    # hreflang: every translation plus x-default (the English page)
    alternates = p.evaluate("""() => Object.fromEntries([...document.querySelectorAll('link[rel="alternate"][hreflang]')]
        .map(l => [l.hreflang, l.href]))""")
    expected = {lang: LIVE + path for lang, path in page["alts"].items()}
    expected["x-default"] = LIVE + page["alts"][MAIN_LANG]
    eq(alternates, expected, "hreflang links")
    assert live_url in alternates.values(), "hreflang must include the page itself"

    ld = json.loads(p.inner_text('script[type="application/ld+json"]'))
    types = [g["@type"] for g in ld["@graph"]]
    assert "WebApplication" in types and "FAQPage" in types, f"JSON-LD types {types}"
    app_ld = next(g for g in ld["@graph"] if g["@type"] == "WebApplication")
    eq(app_ld["inLanguage"], page["lang"], "JSON-LD inLanguage")
    if page["slug"]:
        assert "BreadcrumbList" in types, "no breadcrumbs on exercise page"
    faq = next(g for g in ld["@graph"] if g["@type"] == "FAQPage")
    eq([q["name"] for q in faq["mainEntity"]], p.locator("main h3").all_inner_texts(), "FAQ in JSON-LD vs visible")
    for sel, attr in (('link[rel="stylesheet"]', "href"), ('script[src*="app.js"]', "src")):
        assert "?v=" in p.get_attribute(sel, attr), f"{sel} has no version, browsers may keep a stale copy"
    eq(p.input_value("#plan"), str(page["plan"]), "default plan")
    eq([int(x) for x in p.locator(".presets button").all_inner_texts()], page["presets"], "preset buttons")
    # no text of the other language leaks into the page
    body = p.inner_text("body")
    if page["lang"] == "en":
        assert not any("а" <= ch <= "я" for ch in body.replace("Русский", "").lower()), "Cyrillic text on an English page"


@test("Links and assets on {0[lang]} {0[h1]} open")
def links(page, p, req):
    p.goto(url_of(page))
    hrefs = p.evaluate("""() => [...document.querySelectorAll('a[href], link[href]:not([rel="alternate"]):not([rel="canonical"]), script[src]')]
        .map(e => new URL(e.getAttribute('href') ?? e.getAttribute('src'), location.href))
        .filter(u => u.origin === location.origin && !u.hash)
        .map(u => u.href)""")
    assert hrefs, "no links found"
    bad = [(h, r.status) for h in sorted(set(hrefs)) if (r := req.get(h)).status != 200]
    assert not bad, f"broken: {bad}"
    og = p.get_attribute('meta[property="og:image"]', "content")
    eq(og, f"{LIVE}og/{page['lang']}-{page['id']}.png", "og:image")
    png = req.get(og.replace(LIVE, BASE)).body()
    eq((int.from_bytes(png[16:20], "big"), int.from_bytes(png[20:24], "big")), (1200, 630), "og:image size")
    eq(p.get_attribute('meta[name="twitter:card"]', "content"), "summary_large_image", "twitter:card")
    same_lang = [q for q in PAGES if q["lang"] == page["lang"]]
    if page["slug"]:
        eq(p.locator("main .links a").count(), len(same_lang) - 2, "links to other exercises")
    # the footer links to the translation
    other = {lang: path for lang, path in page["alts"].items() if lang != page["lang"]}
    footer = p.evaluate("""() => Object.fromEntries([...document.querySelectorAll('footer a[hreflang]')]
        .map(a => [a.hreflang, a.href]))""")
    eq(footer, {lang: BASE + path for lang, path in other.items()}, "language switch in footer")


@test("sitemap.xml, robots.txt, manifests, offline list")
def site_files(req):
    r = req.get(BASE + "sitemap.xml")
    eq(r.status, 200, "sitemap status")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "x": "http://www.w3.org/1999/xhtml"}
    urls = ElementTree.fromstring(r.body()).findall("s:url", ns)
    eq([u.find("s:loc", ns).text for u in urls], [LIVE + pg["path"] for pg in PAGES], "sitemap URLs")
    for u, pg in zip(urls, PAGES):
        alts = {x.get("hreflang"): x.get("href") for x in u.findall("x:link", ns)}
        eq(set(alts), {"en", "ru", "x-default"}, f"sitemap alternates of {pg['path'] or '/'}")
    for old in OLD_PATHS:
        assert LIVE + old not in [u.find("s:loc", ns).text for u in urls], f"old address {old} in sitemap"
    robots = req.get(BASE + "robots.txt").text()
    assert "Sitemap: " + LIVE + "sitemap.xml" in robots, "robots.txt has no sitemap line"
    assert "Allow: /" in robots and "Disallow: /\n" not in robots, "robots.txt blocks the site"
    for prefix, lang in (("", "en"), ("ru/", "ru")):
        m = json.loads(req.get(BASE + prefix + "manifest.webmanifest").text())
        eq(m["lang"], lang, f"{prefix}manifest lang")
        for key in ("name", "short_name", "start_url", "display", "icons"):
            assert m.get(key), f"{prefix}manifest has no {key}"
        for icon in m["icons"]:
            eq(req.get(BASE + prefix + icon["src"]).status, 200, f"{prefix}manifest icon {icon['src']}")
    sw = req.get(BASE + "sw.js").text()
    for pg in PAGES:
        if pg["path"]:
            assert f"'{pg['path']}'" in sw, f"sw.js does not precache {pg['path']}"


@test("Old Russian addresses redirect to /ru/")
def redirects(p, req):
    for old, new in OLD_PATHS.items():
        html = req.get(BASE + old).text()
        assert f'<link rel="canonical" href="{LIVE}{new}">' in html, f"{old}: no canonical to {new}"
        p.goto(BASE + old + "#about")
        p.wait_for_url(BASE + new + "#about")
    p.goto(BASE)
    eq(p.evaluate("document.documentElement.lang"), "en", "the root is now English")


# ---------------------------------------------------------------- counter behaviour

@test("Counter keys on {0[lang]} {0[h1]}")
def counter_keys(page, p):
    t = TXT[page["lang"]]
    p.goto(url_of(page))
    plan = page["plan"]
    s = state(p)
    eq((s["count"], s["total"], s["left"]), (0, plan, plan), "initial count/total/left")

    for _ in range(3):
        p.keyboard.press("Space")
    s = state(p)
    eq((s["count"], s["done"], s["left"]), (3, 3, plan - 3), "after 3× space")
    eq(s["bar"], f"{3 / plan * 100:g}%", "progress bar")
    eq(p.evaluate("scrollY"), 0, "space must not scroll the page")

    p.keyboard.press("Backspace")
    eq(state(p)["count"], 2, "after Backspace")
    for _ in range(5):
        p.keyboard.press("Backspace")
    eq(state(p)["count"], 0, "count must not go below 0")

    p.keyboard.press("Enter")
    eq(state(p)["sets"], "", "Enter with 0 must not record a set")

    for _ in range(4):
        p.keyboard.press("Space")
    p.keyboard.press("Enter")
    s = state(p)
    eq(s["count"], 0, "count after finishing a set")
    assert t["sets"].format(n=4) in s["sets"] and t["total"].format(n=4) in s["sets"], f"sets text: {s['sets']!r}"
    p.keyboard.press("Space")
    assert t["total"].format(n=5) in state(p)["sets"], "total must include current set"

    # held key (auto-repeat) and shortcuts must not count
    p.evaluate("""() => {
        document.dispatchEvent(new KeyboardEvent('keydown', {code: 'Space', key: ' ', repeat: true, bubbles: true}));
        document.dispatchEvent(new KeyboardEvent('keydown', {code: 'Space', key: ' ', ctrlKey: true, bubbles: true}));
    }""")
    eq(state(p)["count"], 1, "repeat / Ctrl+Space must be ignored")

    for _ in range(plan - 1):
        p.keyboard.press("Space")
    s = state(p)
    eq((s["count"], s["left"], s["finished"]), (plan, 0, True), "plan reached")
    p.keyboard.press("Space")
    s = state(p)
    eq((s["count"], s["left"]), (plan + 1, 0), "over the plan: left stays 0")
    eq(s["bar"], "100%", "bar capped at 100%")

    p.once("dialog", lambda d: d.dismiss())
    p.keyboard.press("r")
    eq(state(p)["count"], plan + 1, "R cancelled keeps count")
    p.once("dialog", lambda d: d.accept())
    p.keyboard.press("r")
    s = state(p)
    eq((s["count"], s["sets"], s["finished"]), (0, "", False), "R confirmed resets")


@test("Plan field and presets on {0[lang]} {0[h1]}")
def plan_field(page, p):
    p.goto(url_of(page))
    p.click(".presets button >> nth=0")
    eq(state(p)["total"], page["presets"][0], "preset sets plan")
    eq(state(p)["count"], 0, "preset click must not count")

    p.click("#plan")
    p.fill("#plan", "")
    p.keyboard.type("7")
    p.keyboard.press("Space")  # typing in the field must not count
    eq(state(p)["count"], 0, "space inside plan field must not count")
    eq(state(p)["total"], 7, "typed plan")
    p.keyboard.press("Enter")
    eq(p.evaluate("document.activeElement.id"), "", "Enter leaves plan field")
    eq(state(p)["sets"], "", "Enter in plan field must not record a set")

    p.click("#plan")
    p.click(".count")
    eq(state(p)["count"], 0, "first tap after editing plan must not count")
    p.click(".count")
    eq(state(p)["count"], 1, "next tap counts")

    p.click("#plan")
    p.fill("#plan", "")
    p.click(".count")
    eq(p.input_value("#plan"), "7", "empty plan restored")
    p.click("#plan")
    p.fill("#plan", "0")
    p.keyboard.press("Enter")
    eq((p.input_value("#plan"), state(p)["total"]), ("7", 7), "plan 0 rejected")

    before = state(p)["count"]
    p.click("h1")
    p.click(".presets button >> nth=1")
    p.click(".help a")
    eq(state(p)["count"], before, "taps on title, presets and links must not count")


@test("State is saved per exercise and shared by its translations")
def persistence(p):
    pushups_en = next(q for q in PAGES if q["lang"] == "en" and q["id"] == "pushups")
    pushups_ru = next(q for q in PAGES if q["lang"] == "ru" and q["id"] == "pushups")
    squats_en = next(q for q in PAGES if q["lang"] == "en" and q["id"] == "squats")
    p.goto(url_of(pushups_en))
    for _ in range(3):
        p.keyboard.press("Space")
    p.keyboard.press("Enter")
    p.keyboard.press("Space")
    p.reload()
    s = state(p)
    eq(s["count"], 1, "count after reload")
    assert "Sets: 3" in s["sets"], f"sets after reload: {s['sets']!r}"
    p.goto(url_of(squats_en))
    eq(state(p)["count"], 0, "squats have their own count")
    p.goto(url_of(pushups_ru))
    s = state(p)
    eq(s["count"], 1, "the Russian push-up page continues the same workout")
    assert "Подходы: 3" in s["sets"], f"sets in Russian: {s['sets']!r}"


@test("Workout hints ({0})")
def hints(lang, p, req):
    t = TXT[lang]
    url = url_of(home(lang))
    html = req.get(url).text()
    assert t["first"] not in html and 'class="hint"' not in html, "hints must not be in the page HTML (SEO)"
    p.goto(url)
    assert t["intro"] in hint(p) and t["key"] in hint(p), f"intro hint on first visit: {hint(p)!r}"
    p.keyboard.press("Space")
    assert t["first"] in hint(p), f"first-rep hint: {hint(p)!r}"
    for _ in range(4):
        p.keyboard.press("Space")
    assert t["half"] in hint(p), f"half hint at 5 of 10: {hint(p)!r}"
    for _ in range(5):
        p.keyboard.press("Space")
    done = hint(p)
    assert t["done"] in done, f"plan-done hint: {done!r}"
    p.keyboard.press("Enter")
    assert t["set"] in hint(p), f"set hint: {hint(p)!r}"
    for _ in range(5):
        p.keyboard.press("Space")
    assert t["half"] not in hint(p), "half hint must show once per workout"
    for _ in range(5):
        p.keyboard.press("Space")
    assert hint(p) and hint(p) != done, f"plan-done hint repeats with a new line: {hint(p)!r}"
    p.wait_for_function("!document.querySelector('.hint').classList.contains('show')", timeout=7000)

    p.once("dialog", lambda d: d.accept())
    p.keyboard.press("r")
    p.keyboard.press("Space")
    before = state(p)["count"]
    p.click(".hint button")
    eq(state(p)["count"], before, "× must not count")
    eq(hint(p), "", "× hides the hint")
    p.reload()
    for _ in range(10):
        p.keyboard.press("Space")
    eq(hint(p), "", "hints stay off after ×")


@test("Hints get fewer after a few visits")
def hints_regular(p):
    t = TXT["en"]
    p.goto(url_of(home("en")))
    p.evaluate("localStorage.setItem('rep-counter-hints', JSON.stringify({off: false, visits: 5}))")
    p.reload()
    eq(hint(p), "", "no intro for a regular visitor")
    p.keyboard.press("Space")
    eq(hint(p), "", "no first-rep hint for a regular visitor")
    for _ in range(4):
        p.keyboard.press("Space")
    assert t["half"] in hint(p), "half hint stays"
    for _ in range(5):
        p.keyboard.press("Space")
    assert t["done"] in hint(p), "plan-done hint stays"


# Pauses are 15 s on the site; tests shorten them so they don't wait
FAST_PAUSE = """(() => { const st = window.setTimeout;
    window.setTimeout = (f, ms, ...a) => st(f, ms === 15000 ? 150 : ms, ...a); })()"""


@test("Pause hint: only the next rep")
def pause_hint(p):
    p.add_init_script(FAST_PAUSE)
    p.goto(url_of(home("en")))
    p.wait_for_timeout(400)
    assert "Forget the rest" not in hint(p), "no pause hint before the first rep"
    p.keyboard.press("Space")
    p.wait_for_timeout(400)
    assert "Forget the rest" in hint(p) and "1×" in hint(p), f"first pause mentions the 1× button: {hint(p)!r}"
    p.keyboard.press("Space")
    p.wait_for_timeout(400)
    eq(hint(p), "Forget the rest. Just the next one.", "second pause")
    p.evaluate("document.querySelector('.hint').classList.remove('show')")
    p.keyboard.press("Space")
    p.wait_for_timeout(400)
    eq(hint(p), "", "at most two pause hints per workout")


@test("“Just one” mode")
def one_mode(p):
    page = next(q for q in PAGES if q["lang"] == "en" and q["id"] == "pushups")
    p.goto(url_of(page))
    p.click("#one")
    eq(p.get_attribute("#one", "aria-pressed"), "true", "1× is on")
    for sel in (".plan", ".info", ".progress"):
        assert not p.is_visible(sel), f"{sel} must be hidden in “Just one” mode"
    assert "“Just one” mode" in hint(p), f"mode hint: {hint(p)!r}"
    eq(state(p)["count"], 0, "1× must not count")
    for _ in range(5):
        p.keyboard.press("Space")
    eq(hint(p), "5 times just one.", "hint every 5 reps")
    p.reload()
    assert p.evaluate("document.getElementById('app').classList.contains('one')"), "mode is remembered"
    for _ in range(15):
        p.keyboard.press("Space")
    eq(state(p)["count"], 20, "count keeps going")
    eq(hint(p), "20 times just one.", "no goal talk in this mode")
    p.click("#one")
    assert p.is_visible(".plan") and p.is_visible(".info"), "goal is back when the mode is off"


@test("Offer of the other language ({0} browser on {1} page)")
def lang_offer(browser_lang, page_lang, new_page):
    p = new_page(locale=LOCALE[browser_lang])
    page = next(q for q in PAGES if q["lang"] == page_lang and q["id"] == "pushups")
    p.goto(url_of(page))
    if browser_lang == page_lang:
        eq(p.locator(".lang-offer").count(), 0, "no offer when the browser language matches")
        return
    offer = p.locator(".lang-offer")
    assert offer.is_visible(), "offer is shown"
    assert TXT[browser_lang]["offer"] in offer.inner_text(), f"offer text: {offer.inner_text()!r}"
    eq(offer.locator("a").get_attribute("href"), BASE + page["alts"][browser_lang], "offer links to the translation")
    eq(p.evaluate("location.href"), url_of(page), "never redirects by itself")
    offer.locator("button").click()
    eq(state(p)["count"], 0, "closing the offer must not count")
    eq(p.locator(".lang-offer").count(), 0, "× closes the offer")
    p.reload()
    eq(p.locator(".lang-offer").count(), 0, "offer stays closed after ×")


# ---------------------------------------------------------------- offline / mobile / errors

@test("Works offline after first visit")
def offline(ctx):
    p = ctx.new_page()
    p.goto(BASE)
    p.evaluate("navigator.serviceWorker.ready.then(() => true)")
    p.reload()
    assert p.evaluate("navigator.serviceWorker.controller !== null"), "service worker does not control the page"
    cached = p.evaluate("""async () => {
        const names = await caches.keys();
        const c = await caches.open(names[names.length - 1]);
        return (await c.keys()).map(r => r.url);
    }""")
    for f in SW_FILES + [pg["path"] for pg in PAGES if pg["path"]]:
        assert BASE + f in cached, f"not cached: {f or '/'}"
    ctx.set_offline(True)
    try:
        for pg in PAGES:
            p.goto(url_of(pg))
            eq(p.title(), pg["title"], f"offline title of {pg['path'] or '/'}")
            p.keyboard.press("Space")
            assert state(p)["count"] >= 1, "counter works offline"
    finally:
        ctx.set_offline(False)


@test("Phone layout and buttons on {0[lang]} {0[h1]}")
def mobile(page, p):
    p.goto(url_of(page))
    assert TXT[page["lang"]]["intro_touch"] in hint(p), f"phone intro hint: {hint(p)!r}"
    lines = p.evaluate("(() => { const s = document.querySelector('.hint span'); return Math.round(s.getBoundingClientRect().height / parseFloat(getComputedStyle(s).lineHeight)); })()")
    assert lines <= 2, f"intro hint takes {lines} lines on a phone, buttons below would jump"
    # position in the page, not the viewport: taps may scroll by a few pixels
    page_y = "document.querySelector('.controls').getBoundingClientRect().y + scrollY"
    controls_y = p.evaluate(page_y)
    overflow = p.evaluate("document.documentElement.scrollWidth - innerWidth")
    assert overflow <= 0, f"horizontal scroll by {overflow}px"
    assert not p.is_visible(".keys"), "keyboard hints should be hidden on touch screens"
    key = "rep-counter-v1" + (":" + page["store"] if page["store"] else "")
    for n in (88, 888):  # widest 2- and 3-digit numbers must fit on screen
        p.evaluate("([k, n]) => localStorage.setItem(k, JSON.stringify({count: n}))", [key, n])
        p.reload()
        width = p.evaluate("() => { const r = document.createRange(); r.selectNodeContents(document.getElementById('count')); return r.getBoundingClientRect().width; }")
        assert width <= 375 - 16, f"{n} is {width:.0f}px wide, wider than the phone screen"
        assert p.evaluate("document.documentElement.scrollWidth - innerWidth") <= 0, f"{n} causes horizontal scroll"
    p.evaluate("k => localStorage.removeItem(k)", key)
    p.reload()
    box = p.locator(".count").bounding_box()
    assert box["height"] > 150, f"count digits too small: {box['height']:.0f}px"
    assert p.locator("#app").bounding_box()["height"] <= 812 + 1, "counter screen taller than phone"
    p.tap(".count")
    p.tap(".info")
    p.tap(".count")
    eq(state(p)["count"], 3, "taps count on phone")
    eq(p.evaluate(page_y), controls_y, "buttons must not move when the hint changes")

    help_top = p.locator(".help").bounding_box()["y"]
    for btn in p.locator(".controls button:visible").all():
        b = btn.bounding_box()
        assert b["height"] >= 44, f"button {btn.inner_text()!r} too small to tap: {b['height']:.0f}px"
        assert b["y"] + b["height"] <= help_top, f"button {btn.inner_text()!r} overlaps the hint line"

    p.tap("#minus")
    eq(state(p)["count"], 2, "−1 button")
    p.tap("#finish")
    s = state(p)
    eq(s["count"], 0, "Set button resets count")
    assert TXT[page["lang"]]["sets"].format(n=2) in s["sets"], f"Set button records the set: {s['sets']!r}"
    p.tap("#finish")
    eq(state(p)["sets"].count("·"), 0, "Set with 0 must not add an empty set")
    p.tap(".count")
    p.once("dialog", lambda d: d.dismiss())
    p.tap("#reset")
    eq(state(p)["count"], 1, "Reset cancelled keeps count")
    p.once("dialog", lambda d: d.accept())
    p.tap("#reset")
    s = state(p)
    eq((s["count"], s["sets"]), (0, ""), "Reset confirmed resets")

    eq(p.get_attribute("#sound", "aria-pressed"), "true", "sound on by default")
    p.tap("#sound")
    p.reload()
    eq(p.get_attribute("#sound", "aria-pressed"), "false", "sound off is remembered")
    p.tap("#sound")
    eq(p.get_attribute("#sound", "aria-pressed"), "true", "sound back on")
    eq(state(p)["count"], 0, "control buttons must not count as reps")


def main():
    print(f"Testing {BASE}\n")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge")
        errors = []
        contexts = []

        def new_page(**kw):
            ctx = browser.new_context(**kw)
            contexts.append(ctx)
            page = ctx.new_page()
            page.on("console", lambda m: m.type == "error" and errors.append(f"{page.url}: {m.text}"))
            page.on("pageerror", lambda e: errors.append(f"{page.url}: {e}"))
            return page

        def fresh(lang="en", **kw):
            """A new browser profile whose language matches the page, so no language offer appears."""
            while contexts:
                contexts.pop().close()
            return new_page(locale=LOCALE[lang], **kw)

        p = fresh()
        for pg in PAGES:
            seo(pg, p)
            links(pg, p, p.context.request)
        site_files(p.context.request)
        redirects(p, p.context.request)

        for pg in PAGES:
            counter_keys(pg, fresh(pg["lang"]))
            plan_field(pg, fresh(pg["lang"]))

        persistence(fresh())
        for lang in ("en", "ru"):
            p = fresh(lang)
            hints(lang, p, p.context.request)
        hints_regular(fresh())
        pause_hint(fresh())
        one_mode(fresh())
        for browser_lang in ("en", "ru"):
            for page_lang in ("en", "ru"):
                fresh()
                lang_offer(browser_lang, page_lang, new_page)

        while contexts:
            contexts.pop().close()
        ctx = browser.new_context(locale="en-US")
        offline(ctx)
        ctx.close()

        for pg in PAGES:
            mobile(pg, fresh(pg["lang"], viewport={"width": 375, "height": 812}, is_mobile=True, has_touch=True))

        @test("No JavaScript errors in the console")
        def no_errors():
            assert not errors, "\n        ".join(errors[:10])
        no_errors()
        browser.close()

    failed = [r for r in results if not r[0]]
    print(f"\n{len(results) - len(failed)} passed, {len(failed)} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
