import asyncio

from scrape import save_webpage_as_html

if __name__ == "__main__":
    url = "https://unisat.io/runes/market"
    output_file = "example.html"
    selector = "#__next > div.main-container.runes.market > div.mt32.trending-in-brc20 > div.table-container.scroll-x.radius20.border-015 > table > tbody > tr:nth-child(4) > td:nth-child(3) > div"
    save_webpage_as_html(url, output_file, selector)