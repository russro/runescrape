
import scrape

# TODO: put into JSON file
URL = r"https://unisat.io/runes/market?tick=SATOSHI%E2%80%A2NAKAMOTO"
ELEMENTS_PER_PAGE = 20
SELECTORS = [
    f"#rc-tabs-0-panel-1 > div > div.trade-list > div:nth-child({x+1}) > div.content.display-domain.white > div.price-line > span.price"
    for x in range(ELEMENTS_PER_PAGE)
]

def call_prices():
    price_elements = scrape.extract_price_elements(URL, SELECTORS, ELEMENTS_PER_PAGE) # scrape price data at time
    updated_entries = scrape.update_db_entries(URL, price_elements) # update database
    ... # 


if __name__ == "__main__":
    call_prices()
