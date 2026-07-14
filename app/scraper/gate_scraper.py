import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Official GATE website (update if the organizing institute changes)
URL = "https://gate2026.iitg.ac.in/"


def scrape_gate():

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
        "gate",
        "registration",
        "application",
        "notification",
        "important",
        "admit",
        "result",
        "answer key",
        "schedule",
        "information brochure",
        "candidate",
        "exam"
    ]

    ignore = [
        "home",
        "contact",
        "privacy",
        "copyright",
        "login",
        "faq",
        "sitemap",
        "feedback"
    ]

    try:

        response = requests.get(
            URL,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

    except Exception as e:

        print("GATE Scraper Error:", e)
        return []

    soup = BeautifulSoup(response.text, "html.parser")

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

    print("\n========== GATE NOTICES ==========")
    print(f"Found {len(notices)} notices")
    print("=" * 60)

    for i, notice in enumerate(notices, 1):
        print(f"{i}. {notice['title']}")
        print(notice["url"])
        print("-" * 60)

    return notices


if __name__ == "__main__":
    scrape_gate()