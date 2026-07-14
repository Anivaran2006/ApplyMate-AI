import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

URL = "https://www.rrbcdg.gov.in/"


def scrape_railway():

    session = requests.Session()

    retries = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[500, 502, 503, 504]
    )

    session.mount(
        "https://",
        HTTPAdapter(max_retries=retries)
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        )
    }

    notices = []
    seen = set()

    keywords = [
        "cen",
        "notification",
        "recruitment",
        "vacancy",
        "application",
        "exam",
        "result",
        "admit",
        "corrigendum",
        "document verification",
        "medical",
        "rrb"
    ]

    ignore = [
        "home",
        "contact",
        "privacy",
        "feedback",
        "copyright",
        "login",
        "screen reader",
        "sitemap",
        "skip"
    ]

    try:

        response = session.get(
            URL,
            headers=headers,
            timeout=60
        )

        response.raise_for_status()

    except Exception as e:

        print("Railway Scraper Error:", e)
        return []

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    for a in soup.find_all("a"):

        title = " ".join(a.stripped_strings)
        href = a.get("href")

        if not title or not href:
            continue

        title_lower = title.lower()

        if len(title) < 10:
            continue

        if any(word in title_lower for word in ignore):
            continue

        if not any(word in title_lower for word in keywords):
            continue

        full_url = urljoin(URL, href)

        if full_url in seen:
            continue

        seen.add(full_url)

        notices.append({
            "title": title,
            "description": title,
            "url": full_url
        })

    print("\n========== RAILWAY NOTICES ==========")
    print(f"Found {len(notices)} notices")
    print("=" * 60)

    for i, notice in enumerate(notices, 1):
        print(f"{i}. {notice['title']}")
        print(notice["url"])
        print("-" * 60)

    return notices


if __name__ == "__main__":
    scrape_railway()