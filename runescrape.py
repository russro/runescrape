
import os
import json
import re
import validators

from playwright.async_api import async_playwright
from typing import List
from datetime import datetime


# CONFIG VARS
DATABASE = "rune_prices.json"
ELEMENTS_PER_PAGE = 10
SELECTORS = [
    f"#rc-tabs-0-panel-1 > div > div.trade-list > div:nth-child({x+1}) > div.content.display-domain.white > div.price-line > span.price"
    for x in range(ELEMENTS_PER_PAGE)
]


def url_to_ticker(url):
    """Extracts rune ticker name from specific rune UniSat URL.
    """
    name = re.findall(r"tick=([^&]*)", url)[0] # regex pattern to match ticker
    return name

def rune_string_standardizer(rune_name_input: str) -> str:
    """Converts rune name string to standard format.

    >>> rune_string_standardizer("RSIC•GENESIS•RUNE")
    "rsic.genesis.rune"
    """
    try:
        rune_name_standardized = rune_name_input.replace("%E2%80%A2", ".").replace("•", ".").lower()
    except Exception as e:
        return e

    return rune_name_standardized

def rune_name_or_url_standardizer(rune_name_or_url: str) -> str:
    """Converts rune name or URL to standard format.
    """
    rune_name = url_to_ticker(rune_name_or_url) if validators.url(rune_name_or_url) else rune_name_or_url
    rune_name_standardized = rune_string_standardizer(rune_name)

    return rune_name_standardized

def rune_name_standardized_to_url(rune_name_standardized: str) -> str:
    """Converts standardized rune name to UniSat URL.

    >>> rune_name_standardized_to_url("rsic.genesis.rune")
    "https://unisat.io/runes/market?tick=RSIC•GENESIS•RUNE"
    """
    ticker = rune_name_standardized.replace(".", "•").upper()
    url = f"https://unisat.io/runes/market?tick={ticker}"

    return url

async def extract_price_elements(url: str, selectors: List[str] = SELECTORS, elements_per_page: int = ELEMENTS_PER_PAGE):
    """Extracts price data from first page of UniSat rune.
    """
    async with async_playwright() as p:
        # Open and go to URL
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        
        elements = [0]*elements_per_page # preallocate price elements to save

        # Extract and assign all price elements in page
        for i, selector in enumerate(selectors):
            await page.wait_for_selector(selector) # wait for the element in the page to fully load
            element_text = await page.inner_text(selector) # extract to float
            processed_element = float(re.sub("[^0-9.]", "", element_text))

            elements[i] = processed_element # Assign in ascending order

        await browser.close()
    
    return elements

def new_db(file_path: str = DATABASE):
    """Create empty json file.
    """
    with open(file_path, 'w') as outfile:
        json.dump({}, outfile)

def read_db(file_path: str = DATABASE):
    """Read and return contents of json file. Create new json if it does not exist.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except:
        new_db(file_path)
        with open(file_path, 'r') as file:
            data = json.load(file)
    return data

def write_db(file_path: str, data = DATABASE):
    """Write to json file.
    """
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def update_db_entries(url: str, price_elements: List[float] = None, file_path: str = DATABASE):
    """Update database and return updated entries.
    """
    entries = read_db(file_path)

    name = url_to_ticker(url)
    curr_time_checked = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prev_time_checked = (entries[name]['curr_time_checked'] if name in entries and 'curr_time_checked' in entries[name] 
                         else curr_time_checked)
    curr_lowest_price = price_elements[0]
    prev_lowest_price = (entries[name]['curr_lowest_price'] if name in entries and 'curr_lowest_price' in entries[name] 
                         else curr_lowest_price)
    to_add = {
        name: {
            'url': url,
            'prev_hour_checked': 0, # REPLACE
            'curr_hour_checked': 0, # REPLACE
            'prev_hour_lowest_price': 0, # REPLACE
            'curr_hour_lowest_price': 0, # REPLACE
            'curr_hour_low_avg_price': 0, # REPLACE
            'prev_time_checked': prev_time_checked,
            'curr_time_checked': curr_time_checked,
            'prev_lowest_price': prev_lowest_price,
            'curr_lowest_price': curr_lowest_price,
            'curr_low_avg_price': sum(price_elements[0:6])/6,
        }
    }

    entries.update(to_add) # update dictionary

    write_db(file_path, entries)

    return entries



