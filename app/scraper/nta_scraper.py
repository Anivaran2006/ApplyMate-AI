import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://jeemain.nta.nic.in/"


def scrape_nta():

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        )
    }

    try:

        response = requests.get(
            BASE_URL,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

    except Exception as e:

        print("Request Error:", e)
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    notices = []
    seen = set()

    ignore_words = [
        "home",
        "about",
        "contact",
        "privacy",
        "accessibility",
        "menu",
        "login",
        "skip",
        "toggle",
        "contrast",
        "font",
        "highlight",
        "government",
        "ministry",
        "department"
    ]

    keywords = [
        "registration",
        "admit",
        "answer",
        "result",
        "notice",
        "declaration",
        "advisory",
        "application",
        "exam",
        "schedule",
        "city",
        "correction"
    ]

    for a in soup.find_all("a"):

        title = a.get_text(" ", strip=True)
        href = a.get("href")

        if not title or not href:
            continue

        title_lower = title.lower()

        if any(word in title_lower for word in ignore_words):
            continue

        if len(title) < 15:
            continue

        full_url = urljoin(BASE_URL, href)

        if full_url in seen:
            continue

        if not any(word in title_lower for word in keywords):
            continue

        seen.add(full_url)

        notices.append({
            "title": title,
            "url": full_url
        })

    print("\n========== NTA NOTICES ==========\n")

    if not notices:
        print("No notices found.")
        return []

    for i, notice in enumerate(notices, start=1):
        print(f"{i}. {notice['title']}")
        print(notice["url"])
        print("-" * 80)

    return notices


if __name__ == "__main__":
    scrape_nta()