#!/usr/bin/env python3
"""
Google Maps Scraper — Email Extractor
Fetches business websites and extracts contact email addresses.

Author    : Soubarna Karmakar
Copyright : © 2025 Soubarna Karmakar. All rights reserved.
Version   : 2.0
"""

__author__  = "Soubarna Karmakar"
__version__ = "2.0"

import re
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
    _LIBS_OK = True
except ImportError:
    _LIBS_OK = False

# Email regex — RFC-ish but practical
_EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
)

# Common false-positive domains/patterns to skip
_SKIP = [
    "example", "test", "noreply", "no-reply", "sentry",
    "wixpress", "yourdomain", "domain.com", "@2x", ".png",
    ".jpg", ".gif", "placeholder", "schema.org",
]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


class EmailExtractor:
    """
    Scrapes a business website to find a contact email address.
    Checks the home page first, then tries a /contact page.
    """

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        if _LIBS_OK:
            self._session = requests.Session()
            self._session.headers.update(_HEADERS)
        else:
            self._session = None

    def extract(self, url: str) -> str:
        """Return the first credible email found, or empty string."""
        if not _LIBS_OK or not self._session or not url:
            return ""
        try:
            resp = self._session.get(
                url, timeout=self.timeout,
                allow_redirects=True, stream=False
            )
            resp.raise_for_status()
            html  = resp.text
            soup  = BeautifulSoup(html, "html.parser")

            # 1. mailto: links — most reliable
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.lower().startswith("mailto:"):
                    email = href[7:].split("?")[0].strip()
                    if self._valid(email):
                        return email

            # 2. Regex scan of page text
            emails = [e for e in _EMAIL_RE.findall(html) if self._valid(e)]
            if emails:
                return emails[0]

            # 3. Try /contact page
            contact_url = self._find_contact_link(soup, url)
            if contact_url:
                try:
                    r2   = self._session.get(contact_url, timeout=self.timeout)
                    soup2 = BeautifulSoup(r2.text, "html.parser")
                    for a in soup2.find_all("a", href=True):
                        href = a["href"]
                        if href.lower().startswith("mailto:"):
                            email = href[7:].split("?")[0].strip()
                            if self._valid(email):
                                return email
                    emails2 = [e for e in _EMAIL_RE.findall(r2.text) if self._valid(e)]
                    if emails2:
                        return emails2[0]
                except Exception:
                    pass

        except Exception:
            pass
        return ""

    # ── Helpers ────────────────────────────────────────────────────────────────
    @staticmethod
    def _valid(email: str) -> bool:
        if not email or "@" not in email:
            return False
        return not any(skip in email.lower() for skip in _SKIP)

    @staticmethod
    def _find_contact_link(soup, base_url: str) -> str:
        keywords = ["contact", "about", "get-in-touch", "reach-us"]
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True).lower()
            href = a["href"].lower()
            if any(k in text or k in href for k in keywords):
                return urljoin(base_url, a["href"])
        return ""
