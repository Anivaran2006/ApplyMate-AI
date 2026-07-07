"""
ApplyMate AI – NTA Website Scraper
Scrapes https://nta.ac.in for latest notices/announcements.
"""

import hashlib
from datetime import datetime, timezone
from typing import List, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.utils.logger import get_logger

logger = get_logger(__name__)

NTA_BASE_URL = "https://nta.ac.in"
NTA_NOTICE_URL = "https://nta.ac.in/Notices"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def compute_hash(title: str, url: str) -> str:
    """Compute a stable SHA-256 content hash for deduplication."""
    raw = f"{title.strip().lower()}|{url.strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()


async def fetch_page(url: str, timeout: int = 20) -> Optional[str]:
    """Fetch HTML content of a URL. Returns None on failure."""
    try:
        async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=timeout) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP {e.response.status_code} fetching {url}")
    except httpx.RequestError as e:
        logger.error(f"Request error fetching {url}: {e}")
    return None


def parse_nta_notices(html: str) -> List[dict]:
    """
    Parse NTA notice page HTML and extract notice items.
    Returns list of dicts: {title, url, raw_content}
    """
    soup = BeautifulSoup(html, "lxml")
    notices = []

    # NTA uses various table and list structures — try multiple selectors
    # Primary: table rows with links
    rows = soup.select("table tr") or soup.select(".notice-list li") or []

    for row in rows:
        link_tag = row.find("a", href=True)
        if not link_tag:
            continue

        title = link_tag.get_text(strip=True)
        href = link_tag["href"]

        if not title or len(title) < 10:
            continue

        # Resolve relative URLs
        if href.startswith("http"):
            full_url = href
        else:
            full_url = urljoin(NTA_BASE_URL, href)

        raw_content = row.get_text(separator=" ", strip=True)

        notices.append({
            "title": title[:512],
            "url": full_url[:2048],
            "raw_content": raw_content[:5000],
            "content_hash": compute_hash(title, full_url),
        })

    # Fallback: grab all anchor tags from main content area
    if not notices:
        main = soup.select_one("main, #content, .content-area, .container")
        if main:
            for link_tag in main.find_all("a", href=True):
                title = link_tag.get_text(strip=True)
                href = link_tag["href"]
                if not title or len(title) < 15:
                    continue
                if href.startswith("http"):
                    full_url = href
                else:
                    full_url = urljoin(NTA_BASE_URL, href)
                notices.append({
                    "title": title[:512],
                    "url": full_url[:2048],
                    "raw_content": title,
                    "content_hash": compute_hash(title, full_url),
                })

    logger.info(f"NTA scraper found {len(notices)} notices")
    return notices


async def scrape_nta() -> List[dict]:
    """Main entry point: fetch and parse NTA notices page."""
    logger.info("Starting NTA scrape...")
    html = await fetch_page(NTA_NOTICE_URL)
    if not html:
        # Try homepage as fallback
        html = await fetch_page(NTA_BASE_URL)
    if not html:
        logger.error("Failed to fetch NTA website")
        return []
    return parse_nta_notices(html)
