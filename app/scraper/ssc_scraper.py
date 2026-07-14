from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from urllib.parse import urljoin
import time

URL = "https://ssc.gov.in/"


def scrape_ssc():

    options = webdriver.ChromeOptions()

    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager().install()
        ),
        options=options
    )

    notices = []
    seen = set()

    keywords = [
        "notice",
        "notification",
        "exam",
        "result",
        "admit",
        "application",
        "recruitment",
        "vacancy",
        "cgl",
        "chsl",
        "mts",
        "gd",
        "je",
        "cpo"
    ]

    ignore = [
        "home",
        "contact",
        "privacy",
        "login",
        "feedback",
        "copyright",
        "faq",
        "sitemap"
    ]

    try:

        driver.get(URL)

        time.sleep(5)

        links = driver.find_elements(By.TAG_NAME, "a")

        for link in links:

            title = link.text.strip()

            href = link.get_attribute("href")

            if not title or not href:
                continue

            title_lower = title.lower()

            if len(title) < 10:
                continue

            if any(x in title_lower for x in ignore):
                continue

            if not any(x in title_lower for x in keywords):
                continue

            if href in seen:
                continue

            seen.add(href)

            notices.append(
                {
                    "title": title,
                    "description": title,
                    "url": href
                }
            )

    except Exception as e:

        print("SSC Error:", e)

    finally:

        driver.quit()

    print("\n========== SSC NOTICES ==========\n")

    print(f"Found {len(notices)} notices\n")

    for i, notice in enumerate(notices, 1):

        print(f"{i}. {notice['title']}")

        print(notice["url"])

        print("-" * 70)

    return notices


if __name__ == "__main__":
    scrape_ssc()