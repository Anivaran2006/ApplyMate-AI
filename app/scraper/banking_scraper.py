import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://www.ibps.in/"


def scrape_banking():

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
        "notification",
        "notice",
        "exam",
        "result",
        "admit",
        "application",
        "recruitment",
        "crp",
        "po",
        "clerk",
        "so",
        "rrb",
        "vacancy",
        "interview",
        "allotment"
    ]

    ignore = [
        "home",
        "contact",
        "login",
        "privacy",
        "copyright",
        "feedback",
        "sitemap",
        "screen reader",
        "skip",
        "main content"
    ]

    try:

        response = requests.get(
            URL,
            headers=headers,
            timeout=30,
            verify=False
        )

        response.raise_for_status()

    except Exception as e:

        print("Banking Scraper Error:", e)
        return []

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    for a in soup.find_all("a"):

        title = a.get_text(" ", strip=True)
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

        notices.append(
            {
                "title": title,
                "description": title,
                "url": full_url
            }
        )

    print("\n========== BANKING NOTICES ==========")
    print(f"Found {len(notices)} notices")
    print("=" * 60)

    for i, notice in enumerate(notices, 1):
        print(f"{i}. {notice['title']}")
        print(notice["url"])
        print("-" * 60)

    return notices


if __name__ == "__main__":
    scrape_banking()