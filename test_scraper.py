import requests
from bs4 import BeautifulSoup

response = requests.get("https://nta.ac.in")

soup = BeautifulSoup(
    response.text,
    "html.parser"
)

links = soup.find_all("a")

for link in links[:100]:

    text = link.get_text(strip=True)

    href = link.get("href")

    if text:
        print(text)
        print("LINK:", href)
        print("-" * 50)