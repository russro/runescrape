
import scrape

from typing import List

# TODO: put into JSON file
URL = r"https://unisat.io/runes/market?tick=DOG%E2%80%A2GO%E2%80%A2TO%E2%80%A2THE%E2%80%A2MOON"
ELEMENTS_PER_PAGE = 20
SELECTORS = [
    f"#rc-tabs-0-panel-1 > div > div.trade-list > div:nth-child({x+1}) > div.content.display-domain.white > div.price-line > span.price"
    for x in range(ELEMENTS_PER_PAGE)
]

def call_prices(url: str, selectors: List[str], elements_per_page: int):
    """Scrapes prices from Unisat URL; updates and returns prices for tokens.
    """
    price_elements = scrape.extract_price_elements(url, selectors, elements_per_page) # scrape price data at time
    updated_entries = scrape.update_db_entries(url, price_elements) # update database

    return updated_entries


if __name__ == "__main__":
    entries = call_prices(URL, SELECTORS, ELEMENTS_PER_PAGE)
    print(entries)
