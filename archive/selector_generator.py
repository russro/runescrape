
PRICE_ELEMENTS_PER_PAGE = 20
PRICE_SELECTORS = [
    f"#rc-tabs-0-panel-1 > div > div.trade-list > div:nth-child({x+1}) > div.content.display-domain.white > div.price-line > span.price"
    for x in range(PRICE_ELEMENTS_PER_PAGE)
]

print('PRICE_SELECTORS=', PRICE_SELECTORS)