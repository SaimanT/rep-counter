"""Renders the 1200×630 share previews (og/<slug>.png) for every page.

    python site/_build/make_og.py

Run again after changing a page's name or plan. Uses the installed Edge via Playwright.
"""
from html import escape

from playwright.sync_api import sync_playwright

from build import PAGES, SITE

CARD = """<!doctype html><html><head><meta charset="utf-8"><style>
  * {{ margin: 0; box-sizing: border-box; }}
  body {{ width: 1200px; height: 630px; background: #101214; color: #f2f2f2;
    font-family: "Segoe UI", Roboto, Arial, sans-serif; display: flex; padding: 64px 72px; }}
  .text {{ flex: 1; display: flex; flex-direction: column; justify-content: center; gap: 24px; }}
  h1 {{ font-size: 68px; line-height: 1.05; font-weight: 800; }}
  p {{ font-size: 32px; color: #8a9099; line-height: 1.3; }}
  .url {{ font-size: 24px; color: #4ade80; margin-top: 12px; }}
  .counter {{ width: 400px; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
  .n {{ font-size: 260px; font-weight: 800; line-height: 1; font-variant-numeric: tabular-nums; }}
  .info {{ font-size: 30px; color: #8a9099; margin-top: 8px; }}
  .info b {{ color: #f2f2f2; }} .info i {{ color: #4ade80; font-style: normal; font-weight: 700; }}
  .bar {{ width: 340px; height: 14px; background: #23272c; border-radius: 7px; margin-top: 28px; overflow: hidden; }}
  .bar div {{ height: 100%; background: #4ade80; width: {pct}%; }}
</style></head><body>
  <div class="text">
    <h1>{name}<br>онлайн</h1>
    <p>Жмите пробел после каждого повторения — счётчик покажет, сколько осталось</p>
    <div class="url">Бесплатно · без регистрации · работает офлайн</div>
  </div>
  <div class="counter">
    <div class="n">{done}</div>
    <div class="info">из <b>{plan}</b> · осталось <i>{left}</i></div>
    <div class="bar"><div></div></div>
  </div>
</body></html>"""


def main():
    out = SITE / "og"
    out.mkdir(exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge")
        page = browser.new_page(viewport={"width": 1200, "height": 630})
        for p in PAGES:
            plan = p["plan"]
            done = round(plan * 0.6)
            page.set_content(CARD.format(name=escape(p["h1"]), plan=plan, done=done,
                                         left=plan - done, pct=done / plan * 100))
            page.screenshot(path=str(out / f"{p['slug'] or 'home'}.png"))
        browser.close()
    print(f"Rendered {len(PAGES)} previews to {out}")


if __name__ == "__main__":
    main()
