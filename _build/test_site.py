"""End-to-end checks for the site, run in a real browser (installed Edge via Playwright).

    python site/_build/test_site.py                          # live site
    python site/_build/test_site.py http://localhost:8765/site/

Needs: pip install playwright (no browser download — it uses the installed Edge).
"""
import json
import re
import sys
import traceback
from xml.etree import ElementTree

from playwright.sync_api import sync_playwright

sys.path.insert(0, __import__("os").path.dirname(__file__))
from build import PAGES  # noqa: E402

BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://saimant.github.io/rep-counter/").rstrip("/") + "/"
LIVE = "https://saimant.github.io/rep-counter/"
SW_FILES = ["", "index.html", "app.css", "app.js", "manifest.webmanifest", "icon.svg", "icon-192.png", "icon-512.png"]

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
    return BASE + (page["slug"] + "/" if page["slug"] else "")


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


# ---------------------------------------------------------------- SEO / static

@test("SEO: {0[h1]}")
def seo(page, p):
    url = url_of(page)
    resp = p.goto(url)
    eq(resp.status, 200, "HTTP status")
    eq(p.title(), page["title"], "title")
    desc = p.get_attribute('meta[name="description"]', "content")
    eq(desc, page["description"], "description")
    assert 70 <= len(desc) <= 160, f"description length {len(desc)} outside 70–160 (cut off in search results)"
    assert len(p.title()) <= 60, f"title length {len(p.title())} > 60 (cut off in search results)"
    live_url = LIVE + (page["slug"] + "/" if page["slug"] else "")
    eq(p.get_attribute('link[rel="canonical"]', "href"), live_url, "canonical")
    eq(p.get_attribute('meta[property="og:url"]', "content"), live_url, "og:url")
    eq(p.locator("h1").count(), 1, "number of h1")
    eq(p.inner_text("h1"), page["h1"], "h1")
    assert p.get_attribute('meta[name="google-site-verification"]', "content"), "no Google verification tag"
    assert p.get_attribute('meta[name="yandex-verification"]', "content"), "no Yandex verification tag"
    eq(p.get_attribute("html", "lang"), "ru", "lang")
    ld = json.loads(p.inner_text('script[type="application/ld+json"]'))
    types = [g["@type"] for g in ld["@graph"]]
    assert "WebApplication" in types and "FAQPage" in types, f"JSON-LD types {types}"
    if page["slug"]:
        assert "BreadcrumbList" in types, "no breadcrumbs on exercise page"
    faq = next(g for g in ld["@graph"] if g["@type"] == "FAQPage")
    ld_questions = [q["name"] for q in faq["mainEntity"]]
    visible = p.locator("main h3").all_inner_texts()
    eq(ld_questions, visible, "FAQ in JSON-LD vs visible questions")
    for sel, attr in (('link[rel="stylesheet"]', "href"), ('script[src*="app.js"]', "src")):
        assert "?v=" in p.get_attribute(sel, attr), f"{sel} has no version, browsers may keep a stale copy"
    eq(p.input_value("#plan"), str(page["plan"]), "default plan")
    presets = [int(x) for x in p.locator(".presets button").all_inner_texts()]
    eq(presets, page["presets"], "preset buttons")


@test("All links and assets on {0[h1]} open")
def links(page, p, req):
    p.goto(url_of(page))
    hrefs = p.evaluate("""() => [...document.querySelectorAll('a[href], link[href], script[src]')]
        .map(e => new URL(e.getAttribute('href') ?? e.getAttribute('src'), location.href))
        .filter(u => u.origin === location.origin && !u.hash)
        .map(u => u.href)""")
    assert hrefs, "no links found"
    bad = [(h, r.status) for h in sorted(set(hrefs)) if (r := req.get(h)).status != 200]
    assert not bad, f"broken: {bad}"
    og = p.get_attribute('meta[property="og:image"]', "content")
    eq(og, f"{LIVE}og/{page['slug'] or 'home'}.png", "og:image")
    img = req.get(og.replace(LIVE, BASE))
    eq(img.status, 200, "og:image status")
    png = img.body()
    eq((int.from_bytes(png[16:20], "big"), int.from_bytes(png[20:24], "big")), (1200, 630), "og:image size")
    eq(p.get_attribute('meta[name="twitter:card"]', "content"), "summary_large_image", "twitter:card")
    if page["slug"]:
        others = p.locator("main .links a").count()
        eq(others, len(PAGES) - 2, "links to other exercises")


@test("sitemap.xml, robots.txt, manifest")
def site_files(req):
    r = req.get(BASE + "sitemap.xml")
    eq(r.status, 200, "sitemap status")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [e.text for e in ElementTree.fromstring(r.body()).findall("s:url/s:loc", ns)]
    eq(locs, [LIVE + (pg["slug"] + "/" if pg["slug"] else "") for pg in PAGES], "sitemap URLs")
    robots = req.get(BASE + "robots.txt").text()
    assert "Sitemap: " + LIVE + "sitemap.xml" in robots, "robots.txt has no sitemap line"
    assert "Allow: /" in robots and "Disallow: /\n" not in robots, "robots.txt blocks the site"
    m = json.loads(req.get(BASE + "manifest.webmanifest").text())
    for key in ("name", "short_name", "start_url", "display", "icons"):
        assert m.get(key), f"manifest has no {key}"
    for icon in m["icons"]:
        eq(req.get(BASE + icon["src"]).status, 200, f"icon {icon['src']}")
    sw = req.get(BASE + "sw.js").text()
    for pg in PAGES:
        if pg["slug"]:
            assert f"'{pg['slug']}/'" in sw, f"sw.js does not precache {pg['slug']}/"


# ---------------------------------------------------------------- counter behaviour

@test("Counter keys on {0[h1]}")
def counter_keys(page, p):
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
    assert "Подходы: 4" in s["sets"] and "всего за тренировку: 4" in s["sets"], f"sets text: {s['sets']!r}"
    p.keyboard.press("Space")
    assert "всего за тренировку: 5" in state(p)["sets"], "total must include current set"

    # held key (auto-repeat) and shortcuts must not count
    p.evaluate("""() => {
        document.dispatchEvent(new KeyboardEvent('keydown', {code: 'Space', key: ' ', repeat: true, bubbles: true}));
        document.dispatchEvent(new KeyboardEvent('keydown', {code: 'Space', key: ' ', ctrlKey: true, bubbles: true}));
    }""")
    eq(state(p)["count"], 1, "repeat / Ctrl+Space must be ignored")

    # reach the plan
    for _ in range(plan - 1):
        p.keyboard.press("Space")
    s = state(p)
    eq((s["count"], s["left"], s["finished"]), (plan, 0, True), "plan reached")
    p.keyboard.press("Space")
    s = state(p)
    eq((s["count"], s["left"]), (plan + 1, 0), "over the plan: left stays 0")
    eq(s["bar"], "100%", "bar capped at 100%")

    # R: cancel keeps, confirm resets
    p.once("dialog", lambda d: d.dismiss())
    p.keyboard.press("r")
    eq(state(p)["count"], plan + 1, "R cancelled keeps count")
    p.once("dialog", lambda d: d.accept())
    p.keyboard.press("r")
    s = state(p)
    eq((s["count"], s["sets"], s["finished"]), (0, "", False), "R confirmed resets")


@test("Plan field and presets on {0[h1]}")
def plan_field(page, p):
    p.goto(url_of(page))
    p.click(".presets button >> nth=0")
    first = page["presets"][0]
    eq(state(p)["total"], first, "preset sets plan")
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

    # tap on counter while the field is focused only closes it
    p.click("#plan")
    p.click(".count")
    eq(state(p)["count"], 0, "first tap after editing plan must not count")
    p.click(".count")
    eq(state(p)["count"], 1, "next tap counts")

    # empty or invalid plan restores the last valid value
    p.click("#plan")
    p.fill("#plan", "")
    p.click(".count")
    eq(p.input_value("#plan"), "7", "empty plan restored")
    p.click("#plan")
    p.fill("#plan", "0")
    p.keyboard.press("Enter")
    eq((p.input_value("#plan"), state(p)["total"]), ("7", 7), "plan 0 rejected")

    # taps on controls and links don't count
    before = state(p)["count"]
    p.click("h1")
    p.click(".presets button >> nth=1")
    p.click(".help a")
    eq(state(p)["count"], before, "taps on title, presets and links must not count")


@test("State is saved per page")
def persistence(p):
    a, b = url_of(PAGES[1]), url_of(PAGES[2])
    p.goto(a)
    for _ in range(3):
        p.keyboard.press("Space")
    p.keyboard.press("Enter")
    p.keyboard.press("Space")
    p.reload()
    s = state(p)
    eq(s["count"], 1, "count after reload")
    assert "Подходы: 3" in s["sets"], f"sets after reload: {s['sets']!r}"
    p.goto(b)
    eq(state(p)["count"], 0, f"{PAGES[2]['slug']} must have its own count")
    p.goto(a)
    eq(state(p)["count"], 1, "first page keeps its count")


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
    for f in SW_FILES + [pg["slug"] + "/" for pg in PAGES if pg["slug"]]:
        assert BASE + f in cached, f"not cached: {f or '/'}"
    ctx.set_offline(True)
    try:
        for pg in PAGES:
            p.goto(url_of(pg))
            eq(p.title(), pg["title"], f"offline title of {pg['slug'] or 'home'}")
            p.keyboard.press("Space")
            assert state(p)["count"] >= 1, "counter works offline"
    finally:
        ctx.set_offline(False)


@test("Phone layout and buttons on {0[h1]}")
def mobile(page, p):
    p.goto(url_of(page))
    assert "касайтесь экрана" in hint(p), f"phone intro hint: {hint(p)!r}"
    lines = p.evaluate("(() => { const s = document.querySelector('.hint span'); return Math.round(s.getBoundingClientRect().height / parseFloat(getComputedStyle(s).lineHeight)); })()")
    assert lines <= 2, f"intro hint takes {lines} lines on a phone, buttons below would jump"
    # position in the page, not the viewport: taps may scroll by a few pixels
    page_y = "document.querySelector('.controls').getBoundingClientRect().y + scrollY"
    controls_y = p.evaluate(page_y)
    overflow = p.evaluate("document.documentElement.scrollWidth - innerWidth")
    assert overflow <= 0, f"horizontal scroll by {overflow}px"
    assert not p.is_visible(".keys"), "keyboard hints should be hidden on touch screens"
    key = "rep-counter-v1" + (":" + page["slug"] if page["slug"] else "")
    for n in (88, 888):  # widest 2- and 3-digit numbers must fit on screen
        p.evaluate("([k, n]) => localStorage.setItem(k, JSON.stringify({count: n}))", [key, n])
        p.reload()
        box = p.locator(".count").bounding_box()
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

    # every on-screen button is visible, big enough and above the hint line
    help_top = p.locator(".help").bounding_box()["y"]
    for btn in p.locator(".controls button:visible").all():
        b = btn.bounding_box()
        assert b["height"] >= 44, f"button {btn.inner_text()!r} too small to tap: {b['height']:.0f}px"
        assert b["y"] + b["height"] <= help_top, f"button {btn.inner_text()!r} overlaps the hint line"

    p.tap("#minus")
    eq(state(p)["count"], 2, "−1 button")
    p.tap("#finish")
    s = state(p)
    eq(s["count"], 0, "Подход button resets count")
    assert "Подходы: 2" in s["sets"], f"Подход button records the set: {s['sets']!r}"
    p.tap("#finish")
    eq(state(p)["sets"].count("·"), 0, "Подход with 0 must not add an empty set")
    p.tap(".count")
    p.once("dialog", lambda d: d.dismiss())
    p.tap("#reset")
    eq(state(p)["count"], 1, "Сброс cancelled keeps count")
    p.once("dialog", lambda d: d.accept())
    p.tap("#reset")
    s = state(p)
    eq((s["count"], s["sets"]), (0, ""), "Сброс confirmed resets")

    eq(p.get_attribute("#sound", "aria-pressed"), "true", "sound on by default")
    p.tap("#sound")
    p.reload()
    eq(p.get_attribute("#sound", "aria-pressed"), "false", "sound off is remembered")
    p.tap("#sound")
    eq(p.get_attribute("#sound", "aria-pressed"), "true", "sound back on")
    eq(state(p)["count"], 0, "control buttons must not count as reps")


def hint(p):
    return p.evaluate("""() => {
        const h = document.querySelector('.hint');
        return h && h.classList.contains('show') ? h.querySelector('span').textContent : '';
    }""")


@test("Workout hints")
def hints(p, req):
    home = url_of(PAGES[0])
    html = req.get(home).text()
    assert "Не держите счёт" not in html and 'class="hint"' not in html, "hints must not be in the page HTML (SEO)"
    p.goto(home)
    assert "жмите пробел" in hint(p), f"intro hint on first visit: {hint(p)!r}"
    p.keyboard.press("Space")
    assert "Есть первое" in hint(p), f"first-rep hint: {hint(p)!r}"
    for _ in range(4):
        p.keyboard.press("Space")
    assert "Половина" in hint(p), f"half hint at 5 of 10: {hint(p)!r}"
    for _ in range(2):
        p.keyboard.press("Space")
    assert "Осталось три" in hint(p), f"3-left hint at 7 of 10: {hint(p)!r}"
    for _ in range(3):
        p.keyboard.press("Space")
    done = hint(p)
    assert "Сделано" in done, f"plan-done hint: {done!r}"
    p.keyboard.press("Enter")
    assert "Подход записан" in hint(p), f"set hint: {hint(p)!r}"
    for _ in range(5):
        p.keyboard.press("Space")
    assert "Половина" not in hint(p), "half hint must show once per workout"
    for _ in range(5):
        p.keyboard.press("Space")
    assert hint(p) and hint(p) != done, f"plan-done hint repeats with a new line: {hint(p)!r}"
    p.wait_for_function("!document.querySelector('.hint').classList.contains('show')", timeout=7000)

    # ×: hides hints for good and does not count as a rep
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
    p.goto(url_of(PAGES[0]))
    p.evaluate("localStorage.setItem('rep-counter-hints', JSON.stringify({off: false, visits: 5}))")
    p.reload()
    eq(hint(p), "", "no intro for a regular visitor")
    p.keyboard.press("Space")
    eq(hint(p), "", "no first-rep hint for a regular visitor")
    for _ in range(4):
        p.keyboard.press("Space")
    assert "Половина" in hint(p), "half hint stays"
    for _ in range(2):
        p.keyboard.press("Space")
    assert "Осталось три" not in hint(p), "no 3-left hint for a regular visitor"
    for _ in range(3):
        p.keyboard.press("Space")
    assert hint(p), "plan-done hint stays"


def main():
    print(f"Testing {BASE}\n")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge")
        errors = []

        def fresh(**kw):
            ctx = browser.new_context(**kw)
            page = ctx.new_page()
            page.on("console", lambda m: m.type == "error" and errors.append(f"{page.url}: {m.text}"))
            page.on("pageerror", lambda e: errors.append(f"{page.url}: {e}"))
            return ctx, page

        ctx, p = fresh()
        for pg in PAGES:
            seo(pg, p)
            links(pg, p, ctx.request)
        site_files(ctx.request)
        ctx.close()

        for pg in PAGES:
            ctx, p = fresh()
            counter_keys(pg, p)
            ctx.close()
            ctx, p = fresh()
            plan_field(pg, p)
            ctx.close()

        ctx, p = fresh()
        persistence(p)
        ctx.close()

        ctx, p = fresh()
        hints(p, ctx.request)
        ctx.close()
        ctx, p = fresh()
        hints_regular(p)
        ctx.close()

        ctx = browser.new_context()
        offline(ctx)
        ctx.close()

        for pg in PAGES:
            ctx, p = fresh(viewport={"width": 375, "height": 812}, is_mobile=True, has_touch=True)
            mobile(pg, p)
            ctx.close()

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
