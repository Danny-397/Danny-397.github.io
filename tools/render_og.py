#!/usr/bin/env python3
"""Render assets/og-card.html to og-image.png (1200x630, the link-preview card).

The card used to exist only as a PNG with no source, so its "13 weeks" outlived
the site's own figure by months. It now has an HTML source next to the rest of
the site, and tools/check_numbers.py checks the span in it.

USAGE
    python tools/render_og.py

Requires: playwright (pip install playwright; uses the installed Edge).
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

SITE = Path(__file__).resolve().parent.parent


def main() -> None:
    src = (SITE / "assets" / "og-card.html").resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge")
        page = browser.new_page(viewport={"width": 1200, "height": 630})
        page.goto(src)
        page.screenshot(path=str(SITE / "og-image.png"))
        browser.close()
    print("wrote og-image.png")


if __name__ == "__main__":
    main()
