import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://upsc.gov.in/"


def scrape_upsc():

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
        "exam",
        "examination",
        "notification",
        "recruitment",
        "admit",
        "result",
        "answer",
        "application",
        "interview",
        "personality test",
        "civil services",
        "engineering services",
        "nda",
        "cds",
        "cms",
        "ifs",
        "capf"
    ]

    ignore = [
        "home",
        "skip",
        "main content",
        "site map",
        "sitemap",
        "feedback",
        "contact",
        "copyright",
        "accessibility",
        "hindi",
        "english",
        "screen reader",
        "faq",
        "login"
    ]

    try:

        response = requests.get(
            URL,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

    except Exception as e:

        print("UPSC Scraper Error:", e)
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

    print("\n========== UPSC NOTICES ==========")
    print(f"Found {len(notices)} notices")
    print("=" * 60)

    for i, notice in enumerate(notices, 1):
        print(f"{i}. {notice['title']}")
        print(notice["url"])
        print("-" * 60)

    return notices


if __name__ == "__main__":
    scrape_upsc()