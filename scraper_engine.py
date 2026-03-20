#!/usr/bin/env python3
"""
Google Maps Scraper -- Core Scraping Engine
Playwright-based human-like browser automation for Google Maps.

Author    : Soubarna Karmakar
Copyright : (c) 2025 Soubarna Karmakar. All rights reserved.
Version   : 2.0
"""

__author__  = "Soubarna Karmakar"
__version__ = "2.0"

import random
import re
import subprocess
import sys
import time
import unicodedata
from typing import Callable, Optional
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ── Constants ──────────────────────────────────────────────────────────────────
MAPS_SEARCH_URL = "https://www.google.com/maps/search/"
COLUMNS = ["Name", "Address", "Category", "Phone", "Website", "Email", "Rating", "Reviews", "Query"]

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
      Phase 1: scroll the results feed and collect all place URLs.
      Phase 2: visit each URL and extract business details.
    """

    def __init__(
        self,
        *,
        headless: bool = True,
        phone_only: bool = False,
        email_extractor=None,
        on_result:   ResultCB   = None,
        on_status:   StatusCB   = None,
        on_progress: ProgressCB = None,
        on_complete: CompleteCB = None,
    ):
        self.headless        = headless
        self.phone_only      = phone_only
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

    def run(self, queries: list):
        self.is_running = True
        self._stop      = False
        total_found     = 0

        try:
            self._ensure_browser()
            self._status("Launching browser...")

            with sync_playwright() as pw:
                # When the user wants the browser hidden, we launch it visibly
                # but move the window far off-screen instead of using headless=True.
                # True headless mode exposes detectable fingerprints (missing plugins,
                # navigator.headless, etc.) that Google Maps blocks.
                extra_args = []
                if self.headless:
                    extra_args += [
                        "--window-position=-32000,-32000",
                        "--window-size=1366,768",
                    ]
                browser = pw.chromium.launch(
                    headless=False,
                    args=[
                        "--no-sandbox",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-notifications",
                        "--lang=en-US,en",
                    ] + extra_args,
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

                    # NOTE: plain ASCII quotes only -- no smart/curly quotes
                    self._status(
                        '[%d/%d] Collecting: "%s"' % (idx + 1, len(queries), query)
                    )
                    urls = self._collect_urls(page, query)

                    if not urls:
                        self._status('No results found for "%s"' % query, "warning")
                        continue

                    self._status("Extracting data from %d places..." % len(urls))

                    for j, url in enumerate(urls):
                        if self._stop:
                            break
                        self.on_progress(j + 1, len(urls), query)
                        data = self._extract(page, url, query)
                        if data:
                            if self.phone_only and not data.get("Phone"):
                                continue
                            total_found += 1
                            self.on_result(data)
                        self._sleep(0.6, 1.4)

                browser.close()

            if self._stop:
                self._status("Stopped. %d results collected." % total_found, "warning")
            else:
                self._status("Done! %d results extracted." % total_found, "success")

        except Exception as exc:
            self._status("Fatal error: %s" % exc, "error")
        finally:
            self.is_running = False
            self.on_complete(total_found)

    # ── Phase 1 -- collect place URLs ─────────────────────────────────────────
    def _collect_urls(self, page, query: str) -> list:
        search_url = MAPS_SEARCH_URL + quote_plus(query)
        try:
            page.goto(search_url, wait_until="domcontentloaded")
        except Exception:
            return []

        self._sleep(2.5, 3.5)
        self._dismiss_dialogs(page)

        seen: set = set()
        all_urls: list = []
        stale_scrolls = 0
        MAX_STALE     = 5

        while not self._stop:
            # Grab all place links currently in the feed
            try:
                links = page.query_selector_all(
                    'div[role="feed"] a[href*="/maps/place/"]'
                )
                for el in links:
                    href = el.get_attribute("href") or ""
                    clean = href.split("?")[0]
                    if clean and clean not in seen:
                        seen.add(clean)
                        all_urls.append(href)
            except Exception:
                pass

            count_before = len(all_urls)

            # Check for end-of-results text
            try:
                body_text = page.inner_text("body")
                if any(p in body_text for p in _END_PHRASES):
                    self._status("End of list -- %d places found." % len(all_urls))
                    break
            except Exception:
                pass

            # Scroll the feed to load more results
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
                    self._status(
                        "No more new results -- %d places found." % len(all_urls)
                    )
                    break
            else:
                stale_scrolls = 0
                self._status("Found %d places so far..." % len(all_urls))

        return all_urls

    # ── Phase 2 -- extract data from a single place page ──────────────────────
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
            data["Name"] = self._clean(page.inner_text("h1") or "")
        except PWTimeout:
            return None
        if not data["Name"]:
            return None

        # Category ─────────────────────────────────────────────────────────────
        for sel in ["button.DkEaL", ".DkEaL"]:
            try:
                el = page.query_selector(sel)
                if el:
                    data["Category"] = self._clean(el.inner_text() or "")
                    break
            except Exception:
                pass

        # Rating & Reviews ─────────────────────────────────────────────────────
        # Strategy 1 (most reliable): div.F7nice is Google Maps' dedicated
        # rating summary block — contains both the number and review count.
        try:
            f7 = page.query_selector("div.F7nice")
            if f7:
                txt = (f7.inner_text() or "").strip()
                # Text is typically "4.5\n(1,234)" or "4.5(1,234)" or "4.5 (1,234 reviews)"
                r_match = re.search(r'\b([1-5]\.\d)\b', txt)
                v_match = re.search(r'\(([0-9,]+)\)', txt)
                if r_match:
                    data["Rating"] = r_match.group(1)
                if v_match:
                    data["Reviews"] = v_match.group(1).replace(",", "")
        except Exception:
            pass

        # Strategy 2: button that wraps the whole rating widget
        # e.g. <button aria-label="4.5 stars 1,234 reviews">
        if not data["Rating"] or not data["Reviews"]:
            try:
                btn = page.query_selector(
                    'button[aria-label*="star"], button[aria-label*="review"]'
                )
                if btn:
                    label = btn.get_attribute("aria-label") or ""
                    if not data["Rating"]:
                        rm = re.search(r'([1-5]\.\d)\s*star', label, re.IGNORECASE)
                        if rm:
                            data["Rating"] = rm.group(1)
                    if not data["Reviews"]:
                        vm = re.search(r'([0-9,]+)\s*review', label, re.IGNORECASE)
                        if vm:
                            data["Reviews"] = vm.group(1).replace(",", "")
            except Exception:
                pass

        # Strategy 3: aria-label on individual span elements (last resort)
        if not data["Rating"]:
            try:
                # Use query_selector_all and take the FIRST one inside the header,
                # not a random review card further down the page.
                for sel in ['[jslog*="rating"] [aria-label*="star"]',
                            'span[aria-label*=" stars"]']:
                    el = page.query_selector(sel)
                    if el:
                        label = el.get_attribute("aria-label") or ""
                        rm = re.search(r'([1-5]\.\d)', label)
                        if rm:
                            data["Rating"] = rm.group(1)
                            break
            except Exception:
                pass

        if not data["Reviews"]:
            try:
                for sel in ['[jslog*="review"] [aria-label*="review"]',
                            'span[aria-label*=" reviews"]', 'span[aria-label*=" review"]']:
                    el = page.query_selector(sel)
                    if el:
                        label = el.get_attribute("aria-label") or ""
                        vm = re.search(r'([0-9,]+)\s*review', label, re.IGNORECASE)
                        if vm:
                            data["Reviews"] = vm.group(1).replace(",", "")
                            break
            except Exception:
                pass

        # Address, Phone, Website via data-item-id ─────────────────────────────
        try:
            items = page.query_selector_all("[data-item-id]")
            for item in items:
                item_id = item.get_attribute("data-item-id") or ""
                text    = self._clean((item.inner_text() or "").replace("\n", " "))

                if item_id == "address" and not data["Address"]:
                    data["Address"] = text

                elif item_id.startswith("phone:tel:") and not data["Phone"]:
                    # The phone number is encoded in the attribute itself
                    # e.g. data-item-id="phone:tel:+918045678900"
                    data["Phone"] = item_id.split("phone:tel:")[-1].strip()

                elif item_id == "authority" and not data["Website"]:
                    try:
                        link = item.query_selector("a")
                        href = (link.get_attribute("href") if link else "") or ""
                        data["Website"] = href or text
                    except Exception:
                        data["Website"] = text
        except Exception:
            pass

        # Fallback selectors ───────────────────────────────────────────────────
        if not data["Address"]:
            data["Address"] = self._aria_text(page, "Address")

        # Phone fallback: try tel: hyperlink (always present if Google Maps has a number)
        if not data["Phone"]:
            try:
                tel_el = page.query_selector("a[href^='tel:']")
                if tel_el:
                    href = tel_el.get_attribute("href") or ""
                    data["Phone"] = href.replace("tel:", "").strip()
            except Exception:
                pass
        if not data["Phone"]:
            data["Phone"] = self._aria_text(page, "Phone")

        if not data["Website"]:
            try:
                el = page.query_selector("a[data-item-id='authority']")
                if el:
                    data["Website"] = el.get_attribute("href") or ""
            except Exception:
                pass

        # Ensure website has a scheme so email extractor's requests.get() works
        if data["Website"] and not data["Website"].startswith("http"):
            data["Website"] = "https://" + data["Website"]

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
        """Click Accept/Agree consent dialogs if present."""
        for label in ["Accept all", "Accept", "Agree", "I agree"]:
            try:
                btn = page.query_selector('button:has-text("%s")' % label)
                if btn:
                    btn.click()
                    self._sleep(0.8, 1.2)
                    break
            except Exception:
                pass

    def _aria_text(self, page, label: str) -> str:
        try:
            el = page.query_selector(
                '[aria-label*="%s"], [data-tooltip*="%s"]' % (label, label)
            )
            return self._clean(el.inner_text() or "") if el else ""
        except Exception:
            return ""

    def _status(self, msg: str, level: str = "info"):
        self.on_status(msg, level)

    @staticmethod
    def _clean(text: str) -> str:
        """
        Remove non-printable characters and Unicode symbols/icons that Google
        Maps injects into its DOM text (e.g. pin icons, private-use chars).
        Keeps letters, digits, punctuation, and standard whitespace.
        """
        # Normalize (e.g. collapse ligatures, half-width forms)
        text = unicodedata.normalize("NFKC", text)
        # Drop any character whose Unicode category is:
        #   Cc (control), Cf (format), Cs (surrogate), Co (private use),
        #   Cn (unassigned), So (other symbol), Sm (math symbol),
        #   Sk (modifier symbol) — these are the icon/glyph characters.
        cleaned = "".join(
            ch for ch in text
            if unicodedata.category(ch) not in
               {"Cc", "Cf", "Cs", "Co", "Cn", "So", "Sm", "Sk"}
        )
        # Collapse multiple spaces and strip edges
        return re.sub(r" {2,}", " ", cleaned).strip()

    @staticmethod
    def _sleep(lo: float, hi: float):
        time.sleep(random.uniform(lo, hi))

    @staticmethod
    def _ensure_browser():
        """
        Locate Chromium and ensure it is available.

        When running as a PyInstaller bundle (frozen exe):
          - The build script copies the Playwright Chromium browser into
            <exe_dir>/_playwright_browsers/
          - We set PLAYWRIGHT_BROWSERS_PATH so Playwright finds it there.
          - No internet connection required if the browser was bundled.

        When running from source (development):
          - Uses the normal ~/.cache/ms-playwright location.
          - Downloads Chromium on first run if not present.
        """
        import os
        from pathlib import Path

        # Point Playwright to the bundled browsers when frozen
        if getattr(sys, "frozen", False):
            browsers_dir = Path(sys.executable).parent / "_playwright_browsers"
            if browsers_dir.exists():
                os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browsers_dir)

        try:
            with sync_playwright() as pw:
                path = pw.chromium.executable_path
                if not path or not os.path.exists(path):
                    raise FileNotFoundError("Chromium not found")
        except Exception:
            # Browser not found — download it (requires internet)
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                check=True,
            )
