#!/usr/bin/env python3
"""
Google Maps Scraper -- Email Extractor
Fetches business websites and extracts contact email addresses.

Author    : Soubarna Karmakar
Copyright : (c) 2025 Soubarna Karmakar. All rights reserved.
Version   : 2.0
"""

__author__  = "Soubarna Karmakar"
__version__ = "2.0"

import re
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
    _LIBS_OK = True
except ImportError:
    _LIBS_OK = False

# Email regex -- RFC-ish but practical
_EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
)

# Common false-positive domains/patterns to skip
_SKIP = [
    "example", "test", "noreply", "no-reply", "sentry",
    "wixpress", "yourdomain", "domain.com", "@2x", ".png",
    ".jpg", ".gif", "placeholder", "schema.org", "email.com",
    "acme.com", "company.com", "yoursite", "website.com",
    "wordpress", "w3.org", "googleapis", "gstatic",
]

# Contact page slug patterns to try (appended to base domain)
_CONTACT_SLUGS = [
    "/contact", "/contact-us", "/contactus",
    "/about", "/about-us", "/aboutus",
    "/reach-us", "/reach", "/get-in-touch",
    "/support", "/help",
]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
}


class EmailExtractor:
    """
    Scrapes a business website to find a contact email address.
    Checks the home page first, then tries common contact page URLs.
    """

    def __init__(self, timeout: int = 12):
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
        # Ensure the URL has a scheme
        if not url.startswith("http"):
            url = "https://" + url

        # 1. Try home page
        email = self._scan_url(url)
        if email:
            return email

        # 2. Try contact pages -- both from link discovery and direct slug probing
        base = self._base_url(url)
        for slug in _CONTACT_SLUGS:
            candidate = base + slug
            if candidate == url:
                continue
            email = self._scan_url(candidate)
            if email:
                return email

        return ""

    # ── Internal ────────────────────────────────────────────────────────────────

    def _scan_url(self, url: str) -> str:
        """Fetch url, parse HTML, return first valid email or ''."""
        try:
            resp = self._session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                stream=False,
                verify=True,
            )
            # Do NOT raise_for_status -- many sites return 403/503 but still
            # contain readable HTML with contact info in the body.
            html = resp.text
        except requests.exceptions.SSLError:
            # Retry without SSL verification for sites with bad certs
            try:
                resp = self._session.get(
                    url, timeout=self.timeout,
                    allow_redirects=True, stream=False, verify=False,
                )
                html = resp.text
            except Exception:
                return ""
        except Exception:
            return ""

        soup = BeautifulSoup(html, "html.parser")

        # Priority 1: mailto: links -- most reliable
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.lower().startswith("mailto:"):
                email = href[7:].split("?")[0].strip()
                if self._valid(email):
                    return email

        # Priority 2: regex scan of raw HTML source
        emails = [e for e in _EMAIL_RE.findall(html) if self._valid(e)]
        if emails:
            # Prefer emails whose domain matches the site domain
            domain = urlparse(url).hostname or ""
            domain = domain.lstrip("www.")
            for e in emails:
                if domain and domain in e:
                    return e
            return emails[0]

        return ""

    @staticmethod
    def _base_url(url: str) -> str:
        """Return scheme + netloc, e.g. 'https://example.com'."""
        p = urlparse(url)
        return "%s://%s" % (p.scheme or "https", p.netloc or p.path.split("/")[0])

    @staticmethod
    def _valid(email: str) -> bool:
        if not email or "@" not in email:
            return False
        local, _, domain = email.partition("@")
        if len(local) < 2 or "." not in domain:
            return False
        return not any(skip in email.lower() for skip in _SKIP)
