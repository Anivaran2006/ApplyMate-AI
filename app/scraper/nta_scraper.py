import requests
from bs4 import BeautifulSoup

URL = "https://nta.ac.in"

def get_latest_notification():

    response = requests.get(URL)

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    links = soup.find_all("a")

    for link in links:

        href = link.get("href")

        if href and "/Download/Notice/" in href:

            full_link = f"https://nta.ac.in{href}"

            return {
                "title": href.split("/")[-1],
                "link": full_link
            }

    return {
        "title": "No Notice Found",
        "link": URL
    }