
import os
import json
import re
import validators

from playwright.async_api import async_playwright
from playwright.async_api import Page, Browser
from typing import List, Union, Callable
from datetime import datetime


# Config variables
PRICE_DATABASE_PATH = os.getenv('PRICE_DATABASE_PATH')
NICKNAME_DATABASE_PATH = os.getenv('NICKNAME_DATABASE_PATH')
ELEMENTS_PER_PAGE = 10
SELECTORS = [
    f"#rc-tabs-0-panel-1 > div > div.trade-list > div:nth-child({x+1}) > div.content.display-domain.white > div.price-line > span.price"
    for x in range(ELEMENTS_PER_PAGE)
]


# TODO: consolidate functions into class
def url_to_ticker(unisat_url):
    """Extracts rune ticker name from specific rune UniSat URL.
    """
    name = re.findall(r"tick=([^&]*)", unisat_url)[0] # regex pattern to match ticker
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

# TODO: consolidate functions into class
async def extract_prices(selectors: List[int], page: Page) -> List[float]:
    """Extract price elements from UniSat rune marketplace page.
    """
    elements = [0]*len(selectors) # preallocate price elements to save

    for i, selector in enumerate(selectors):
        try:
            await page.wait_for_selector(selector) # wait for the element in the page to fully load
            element_text = await page.inner_text(selector) # extract to float
            processed_element = float(re.sub("[^0-9.]", "", element_text))

            elements[i] = processed_element # Assign in ascending order
        except Exception as e:
            # await browser.close() # TODO: check if this is necessary
            return e
        
    return elements

async def extract_mint_amount(selectors: List[int], page: Page) -> List[int]:
    """Extracts mint amount for a specified rune from UniSat rune detail page.
    """
    return

    return elements

async def extract_elements(url: str, extract_func: Callable[[List[int], Page], List[Union[int, float]]],
                           selectors: List[str] = SELECTORS, ) -> List[float]:
    """Extracts elements using specified extract function.
    """
    async with async_playwright() as p:
        # Open and go to URL
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        
        elements = extract_func(selectors, page)

        await browser.close()
    
    return elements

# TODO: consolidate functions into class within its own file
def new_json(file_path: str):
    """Create empty json file.
    """
    with open(file_path, 'w') as outfile:
        json.dump({}, outfile)

def read_json(file_path: str):
    """Read and return contents of json file. Create new json if it does not exist.
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

def update_db_entries(unisat_url: str, file_path: str, price_elements: List[float] = None):
    """Update database and return updated entries.
    """
    # Load price db
    entries = read_json(file_path)

    # Extract standardized name and standardized url
    rune_name_standardized = rune_string_standardizer(url_to_ticker(unisat_url))
    rune_url_standardized = rune_name_standardized_to_url(rune_name_standardized)

    # Configure variables to store in db
    curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    to_add = {
        rune_name_standardized: {
            'url': rune_url_standardized,
            'tokens_per_mint': 0, # TODO: replace the 0
            'price_array': [],
            'price_timestamps': []
        }
    }

    entries.update(to_add) # update dictionary

    write_json(file_path, entries)

    return entries



