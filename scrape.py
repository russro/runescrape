
import os
import json
import re

from playwright.sync_api import sync_playwright
from typing import List


def read_json(file_path: str):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def write_json(file_path: str, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def update_db_entries(url: str, price_elements: List[float] = None, file_path: str = "rune_prices.json"):
    """Update database.
    """
    # Create new file if it does not exist.
    if not os.path.exists(file_path):
        with open(file_path, 'w') as outfile:
            json.dump({}, outfile)

    # Read and update file
    entries = read_json(file_path)
    name = re.findall(r"(?<=tick=).*", url)[0] # regex pattern to match ticker
    last_time_checked = ...
    prev_lowest_price = ...
    to_add = {name: {
        'url': url,
        'last_time_checked': last_time_checked,
        'prev_lowest_price': prev_lowest_price,
        'curr_lowest_price': price_elements[0],
        'curr_low_avg_price': sum(price_elements[0:6])/6
        }
    }
    entries.update(to_add)

    write_json(file_path, entries)

    return entries

def extract_price_elements(url: str, selectors: List[str], elements_per_page: int = 20):
    """Extracts price data from first page of UniSat rune.
    """
    with sync_playwright() as p:
        # Open and go to URL
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        
        elements = [0]*elements_per_page # preallocate price elements to save

        # Extract and assign all price elements in page
        for i, selector in enumerate(selectors):
            page.wait_for_selector(selector) # wait for the element in the page to fully load
            element_text = page.inner_text(selector) # extract to float
            processed_element = float(re.sub("[^0-9.]", "", element_text))

            print("Element text:", processed_element)
            print(type(processed_element))

            elements[i] = element_text # Assign in ascending order

        browser.close()
    
    return elements

