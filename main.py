from scrape import extract_price_elements

# TODO: put into JSON file
URL = r"https://unisat.io/runes/market?tick=SATOSHI%E2%80%A2NAKAMOTO"
ELEMENTS_PER_PAGE = 20
SELECTORS = [
    f"#rc-tabs-0-panel-1 > div > div.trade-list > div:nth-child({x+1}) > div.content.display-domain.white > div.price-line > span.price"
    for x in range(ELEMENTS_PER_PAGE)
]


if __name__ == "__main__":
    extract_price_elements(URL, ELEMENTS_PER_PAGE, SELECTORS)