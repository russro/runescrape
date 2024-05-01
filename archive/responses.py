
import runescrape

from typing import List


URL = r"https://unisat.io/runes/market?tick=SATOSHI%E2%80%A2NAKAMOTO"
ELEMENTS_PER_PAGE = 20
SELECTORS = [
    f"#rc-tabs-0-panel-1 > div > div.trade-list > div:nth-child({x+1}) > div.content.display-domain.white > div.price-line > span.price"
    for x in range(ELEMENTS_PER_PAGE)
]


async def call_prices(url: str, selectors: List[str], elements_per_page: int):
    """Scrapes prices from Unisat URL; updates and returns prices for tokens.
    """
    price_elements = await runescrape.extract_price_elements(url, selectors, elements_per_page) # scrape price data at time
    updated_entries = runescrape.update_db_entries(url, price_elements) # update database

    return updated_entries

async def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return 'Well, you\'re awfully silent...'
    elif 'hello' in lowered:
        return 'Hello there!'
    elif 'sold' in lowered:
        return 'PAPERHANDS'
    elif 'price' in lowered:
        return await call_prices(URL, SELECTORS, ELEMENTS_PER_PAGE)