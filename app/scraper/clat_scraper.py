import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://consortiumofnlus.ac.in/"


def scrape_clat():

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
        "clat",
        "notification",
        "registration",
        "application",
        "exam",
        "result",
        "answer key",
        "admit",
        "important",
        "schedule",
        "candidate",
        "press release",
        "notice",
        "counselling",
        "merit",
        "admission"
    ]

    ignore = [
        "home",
        "about",
        "contact",
        "login",
        "privacy",
        "copyright",
        "feedback",
        "sitemap",
        "committee",
        "executive",
        "objectives",
        "bye laws",
        "tender",
        "career",
        "gallery"
    ]

    try:

        response = requests.get(
            URL,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

    except Exception as e:

        print("CLAT Scraper Error:", e)
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

    print("\n========== CLAT NOTICES ==========")
    print(f"Found {len(notices)} notices")
    print("=" * 60)

    for i, notice in enumerate(notices, 1):
        print(f"{i}. {notice['title']}")
        print(notice["url"])
        print("-" * 60)

    return notices


if __name__ == "__main__":
    scrape_clat()