from app.scraper.nta_scraper import scrape_nta
from app.scraper.gate_scraper import scrape_gate
from app.scraper.upsc_scraper import scrape_upsc
from app.scraper.ssc_scraper import scrape_ssc
from app.scraper.railway_scraper import scrape_railway
from app.scraper.banking_scraper import scrape_banking
from app.scraper.cat_scraper import scrape_cat
from app.scraper.clat_scraper import scrape_clat


def scrape_all():

    all_notices = []

    scrapers = [
        scrape_nta,
        scrape_gate,
        scrape_upsc,
        scrape_ssc,
        scrape_railway,
        scrape_banking,
        scrape_cat,
        scrape_clat
    ]

    for scraper in scrapers:

        try:

            notices = scraper()

            if notices:
                all_notices.extend(notices)

            print(f"✅ {scraper.__name__}: {len(notices)} notices")

        except Exception as e:

            print(f"❌ {scraper.__name__}: {e}")

    return all_notices