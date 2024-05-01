
import os
import json
import re

from playwright.async_api import async_playwright
from typing import List
from datetime import datetime


ELEMENTS_PER_PAGE = 20
SELECTORS = [
    f"#rc-tabs-0-panel-1 > div > div.trade-list > div:nth-child({x+1}) > div.content.display-domain.white > div.price-line > span.price"
    for x in range(ELEMENTS_PER_PAGE)
]


def new_json(file_path: str):
    """Create empty json file.
    """
    with open(file_path, 'w') as outfile:
        json.dump({}, outfile)

def read_json(file_path: str):
    """Read and return contents of json file.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except:
        new_json(file_path)
        with open(file_path, 'r') as file:
            data = json.load(file)
    return data

def write_json(file_path: str, data):
    """Write to json file.
    """
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def read_curr_entries(url: str, price_elements: List[float] = None, file_path: str = "rune_prices.json"):
    """Read database and return updated dictionary (without updating the db).
    """
    # Create new file if it does not exist.
    if not os.path.exists(file_path):
        new_json(file_path)

    # Read and update file
    entries = read_json(file_path)

    name = re.findall(r"(?<=tick=).*", url)[0] # regex pattern to match ticker
    curr_time_checked = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prev_time_checked = (entries[name]['curr_time_checked'] if name in entries and 'curr_time_checked' in entries[name] 
                         else curr_time_checked)
    curr_lowest_price = price_elements[0]
    prev_lowest_price = (entries[name]['curr_lowest_price'] if name in entries and 'curr_lowest_price' in entries[name] 
                         else curr_lowest_price)
    to_add = {
        name: {
            'url': url,
            # 'prev_hour_checked': ...,
            'prev_time_checked': prev_time_checked,
            # 'curr_hour_checked': ...,
            'curr_time_checked': curr_time_checked,
            'prev_lowest_price': prev_lowest_price,
            'curr_lowest_price': curr_lowest_price,
            'curr_low_avg_price': sum(price_elements[0:6])/6,
        }
    }

    entries.update(to_add) # update dictionary

    return entries

def update_db_entries(url: str, price_elements: List[float] = None, file_path: str = "rune_prices.json"):
    """Update database and return updated entries.
    """
    entries = curr_entries(url, price_elements, file_path)
    write_json(file_path, entries)

    return entries

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
