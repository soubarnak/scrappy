#!/usr/bin/env python3
"""
Google Maps Scraper — Core Scraping Engine
Playwright-based human-like browser automation for Google Maps.

Author    : Soubarna Karmakar
Copyright : © 2025 Soubarna Karmakar. All rights reserved.
Version   : 2.0
"""

__author__  = "Soubarna Karmakar"
__version__ = "2.0"

import random
import re
import subprocess
import sys
import time
from typing import Callable, Optional
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ── Constants ──────────────────────────────────────────────────────────────────
MAPS_SEARCH_URL = "https://www.google.com/maps/search/"
COLUMNS = ["Name", "Address", "Category", "Phone", "Website", "Email", "Query"]

_END_PHRASES = [
    "You've reached the end of the list",
    "No results for",
    "didn't match any places",
]

# ── Type aliases ───────────────────────────────────────────────────────────────
ResultCB   = Callable[[dict], None]
StatusCB   = Callable[[str, str], None]
ProgressCB = Callable[[int, int, str], None]
CompleteCB = Callable[[int], None]


class ScraperEngine:
    """
    Two-phase Google Maps scraper.
      Phase 1 — scroll the results feed and collect all place URLs.
      Phase 2 — visit each URL and extract business details.
    """

    def __init__(
        self,
        *,
        headless: bool = True,
        email_extractor=None,
        on_result:   ResultCB   = None,
        on_status:   StatusCB   = None,
        on_progress: ProgressCB = None,
        on_complete: CompleteCB = None,
    ):
        self.headless        = headless
        self.email_extractor = email_extractor
        self.on_result       = on_result   or (lambda d: None)
        self.on_status       = on_status   or (lambda m, l: None)
        self.on_progress     = on_progress or (lambda c, t, q: None)
        self.on_complete     = on_complete or (lambda t: None)

        self.is_running = False
        self._stop      = False

    # ── Public API ─────────────────────────────────────────────────────────────
    def stop(self):
        self._stop = True

    def run(self, queries: list[str]):
        self.is_running = True
        self._stop      = False
        total_found     = 0

        try:
            self._ensure_browser()
            self._status("Launching browser…")

            with sync_playwright() as pw:
                browser = pw.chromium.launch(
                    headless=self.headless,
                    args=[
                        "--no-sandbox",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-notifications",
                        "--lang=en-US,en",
                    ],
                )
                ctx = browser.new_context(
                    viewport={"width": 1366, "height": 768},
                    locale="en-US",
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"
                    ),
                )
                # Stealth: hide automation fingerprint
                ctx.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'languages', {get: () => ['en-US','en']});
                    window.chrome = { runtime: {} };
                """)
                page = ctx.new_page()
                page.set_default_timeout(15_000)

                for idx, query in enumerate(queries):
                    if self._stop:
                        break
                    query = query.strip()
                    if not query:
                        continue

                    self._status(f"[{idx+1}/{len(queries)}] Collecting: "{query}"")
                    urls = self._collect_urls(page, query)

                    if not urls:
                        self._status(f'No results found for "{query}"', "warning")
                        continue

                    self._status(f"Extracting data from {len(urls)} places…")

                    for j, url in enumerate(urls):
                        if self._stop:
                            break
                        self.on_progress(j + 1, len(urls), query)
                        data = self._extract(page, url, query)
                        if data:
                            total_found += 1
                            self.on_result(data)
                        self._sleep(0.6, 1.4)

                browser.close()

            if self._stop:
                self._status(f"Stopped. {total_found} results collected.", "warning")
            else:
                self._status(f"✓ Done! {total_found} results extracted.", "success")

        except Exception as exc:
            self._status(f"Fatal error: {exc}", "error")
        finally:
            self.is_running = False
            self.on_complete(total_found)

    # ── Phase 1 — collect place URLs ───────────────────────────────────────────
    def _collect_urls(self, page, query: str) -> list[str]:
        search_url = MAPS_SEARCH_URL + quote_plus(query)
        try:
            page.goto(search_url, wait_until="domcontentloaded")
        except Exception:
            return []

        self._sleep(2.5, 3.5)
        self._dismiss_dialogs(page)

        seen: set[str] = set()
        all_urls:  list[str] = []
        stale_scrolls = 0
        MAX_STALE     = 5

        while not self._stop:
            # Grab all place links currently in the feed
            try:
                links = page.query_selector_all('div[role="feed"] a[href*="/maps/place/"]')
                for el in links:
                    href = el.get_attribute("href") or ""
                    clean = href.split("?")[0]
                    if clean and clean not in seen:
                        seen.add(clean)
                        all_urls.append(href)
            except Exception:
                pass

            count_before = len(all_urls)

            # Check for end-of-results
            try:
                body_text = page.inner_text("body")
                if any(p in body_text for p in _END_PHRASES):
                    self._status(f"End of list — {len(all_urls)} places found.")
                    break
            except Exception:
                pass

            # Scroll the feed
            try:
                page.evaluate(
                    """() => {
                        const feed = document.querySelector('div[role="feed"]');
                        if (feed) feed.scrollTop = feed.scrollHeight;
                    }"""
                )
                self._sleep(1.8, 2.8)
            except Exception:
                break

            if len(all_urls) == count_before:
                stale_scrolls += 1
                if stale_scrolls >= MAX_STALE:
                    self._status(f"No more new results — {len(all_urls)} places found.")
                    break
            else:
                stale_scrolls = 0
                self._status(f"Found {len(all_urls)} places so far…")

        return all_urls

    # ── Phase 2 — extract data from a place page ───────────────────────────────
    def _extract(self, page, url: str, query: str) -> Optional[dict]:
        try:
            page.goto(url, wait_until="domcontentloaded")
            self._sleep(1.8, 2.5)
        except Exception:
            return None

        data = {col: "" for col in COLUMNS}
        data["Query"] = query

        # Name ─────────────────────────────────────────────────────────────────
        try:
            page.wait_for_selector("h1", timeout=8_000)
            data["Name"] = (page.inner_text("h1") or "").strip()
        except PWTimeout:
            return None
        if not data["Name"]:
            return None

        # Category ─────────────────────────────────────────────────────────────
        for sel in ["button.DkEaL", ".DkEaL"]:
            try:
                el = page.query_selector(sel)
                if el:
                    data["Category"] = (el.inner_text() or "").strip()
                    break
            except Exception:
                pass

        # Info items (address / phone / website) ───────────────────────────────
        try:
            items = page.query_selector_all("[data-item-id]")
            for item in items:
                item_id = item.get_attribute("data-item-id") or ""
                text    = (item.inner_text() or "").strip().replace("\n", ", ")

                if item_id == "address" and not data["Address"]:
                    data["Address"] = text

                elif item_id.startswith("phone:tel:") and not data["Phone"]:
                    data["Phone"] = text.split(",")[0]

                elif item_id == "authority" and not data["Website"]:
                    try:
                        link = item.query_selector("a")
                        data["Website"] = (
                            link.get_attribute("href") if link else text
                        ) or text
                    except Exception:
                        data["Website"] = text
        except Exception:
            pass

        # Fallback selectors ───────────────────────────────────────────────────
        if not data["Address"]:
            data["Address"] = self._aria_text(page, "Address")
        if not data["Phone"]:
            data["Phone"]   = self._aria_text(page, "Phone")
        if not data["Website"]:
            try:
                el = page.query_selector("a[data-item-id='authority']")
                if el:
                    data["Website"] = el.get_attribute("href") or ""
            except Exception:
                pass

        # Email (optional) ─────────────────────────────────────────────────────
        if self.email_extractor and data["Website"]:
            try:
                data["Email"] = self.email_extractor.extract(data["Website"]) or "N/A"
            except Exception:
                data["Email"] = "N/A"
        else:
            data["Email"] = "N/A"

        return data

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _dismiss_dialogs(self, page):
        """Click 'Accept' / 'Agree' consent dialogs if present."""
        for text in ["Accept all", "Accept", "Agree", "I agree"]:
            try:
                btn = page.query_selector(f'button:has-text("{text}")')
                if btn:
                    btn.click()
                    self._sleep(0.8, 1.2)
                    break
            except Exception:
                pass

    def _aria_text(self, page, label: str) -> str:
        try:
            el = page.query_selector(
                f'[aria-label*="{label}"], [data-tooltip*="{label}"]'
            )
            return (el.inner_text() or "").strip() if el else ""
        except Exception:
            return ""

    def _status(self, msg: str, level: str = "info"):
        self.on_status(msg, level)

    @staticmethod
    def _sleep(lo: float, hi: float):
        time.sleep(random.uniform(lo, hi))

    @staticmethod
    def _ensure_browser():
        """Download Chromium if not present (safe in frozen PyInstaller builds)."""
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as pw:
                path = pw.chromium.executable_path
                if not path or not __import__("os").path.exists(path):
                    raise FileNotFoundError
        except Exception:
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                check=True,
            )
