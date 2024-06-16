
import os
import json
import re
import validators
import random
import asyncio
import numbers

from playwright.async_api import async_playwright
from playwright.async_api import Page, Browser
from typing import List, Tuple, Union, Callable
from datetime import datetime


# Config variables
PRICE_DATABASE_PATH = os.getenv('PRICE_DATABASE_PATH')
NICKNAME_DATABASE_PATH = os.getenv('NICKNAME_DATABASE_PATH')

PRICE_ELEMENTS_PER_PAGE = 1
PRICE_SELECTOR_LIST = [
    f"#rc-tabs-0-panel-1 > div > div.trade-list > div:nth-child({x+1}) > div.content.display-domain.white > div.price-line > span.price"
    for x in range(PRICE_ELEMENTS_PER_PAGE)
    ]
VOLUME_SELECTOR_LIST = [
    "#__next > div.main-container.runes.market > div.brc-20-market > div.mt32.flex-row-stretch.gap24 > div > div.runes-market-info-container.mt24 > div:nth-child(1) > div.flex-row-v-center.gap-4"
    ]
PRICE_VOLUME_SELECTOR_LIST = PRICE_SELECTOR_LIST + VOLUME_SELECTOR_LIST
MINT_AMOUNT_SELECTOR_LIST = [
    "#__next > div.main-container.brc-20.brc-20-item-page.runes > div > div:nth-child(3) > div.ant-card-body > div > div.ml24.flex-column.gap-16 > div:nth-child(3) > div.font14.white085"
    ]

PRICE_ARRAY_LEN = 20


# TODO: consolidate functions into class
def prices_url_to_ticker(unisat_url):
    """Extracts rune ticker name from specific rune UniSat URL.
    """
    name = re.findall(r"tick=([^&]*)", unisat_url)[0] # regex pattern to match ticker
    return name

def rune_name_standardizer(rune_name_input: str) -> str:
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
    rune_name = prices_url_to_ticker(rune_name_or_url) if validators.url(rune_name_or_url) else rune_name_or_url
    rune_name_standardized = rune_name_standardizer(rune_name)

    return rune_name_standardized

def rune_name_std_to_ticker(rune_name_standardized: str) -> str:
    """Converts standardized rune name to ticker name.
    """
    return rune_name_standardized.replace(".", "•").upper()

def rune_name_std_to_prices_url(rune_name_standardized: str) -> str:
    """Converts standardized rune name to UniSat URL.

    >>> rune_name_standardized_to_url("rsic.genesis.rune")
    "https://unisat.io/runes/market?tick=RSIC•GENESIS•RUNE"
    """
    ticker = rune_name_std_to_ticker(rune_name_standardized)
    url = f"https://unisat.io/runes/market?tick={ticker}"

    return url

def rune_name_std_to_mint_amt_url(rune_name_standardized: str) -> str:
    """Converts standardized rune name to UniSat URL.

    >>> rune_name_standardized_to_url("rsic.genesis.rune")
    "https://unisat.io/runes/detail/RSIC•GENESIS•RUNE"
    """
    ticker = rune_name_standardized.replace(".", "•").upper()
    url = f"https://unisat.io/runes/detail/{ticker}"

    return url


# TODO: consolidate functions into class
async def extract_prices_or_volume(selectors: List[int], page: Page) -> List[float]:
    """Extract price elements from UniSat rune marketplace page.
    """
    elements = [0]*len(selectors) # preallocate price elements to save

    for i, selector in enumerate(selectors):
        try:
            await page.wait_for_selector(selector) # wait for the element in the page to fully load
            element_text = await page.inner_text(selector) # extract to float
            processed_element = float(re.sub("[^0-9.]", "", element_text))

            elements[i] = processed_element # assign in ascending order
        except Exception as e:
            print(e)
            return e
        
    return elements

async def extract_mint_amount(selectors: List[int], page: Page) -> float:
    """Extracts mint amount for a specified rune from UniSat rune detail page.
    """
    
    selector = selectors[0]
    
    try:
        await page.wait_for_selector(selector) # wait for the element in the page to fully load
        element_text = await page.inner_text(selector) # extract to float
        processed_element = float(re.sub("[^0-9.]", "", element_text))

        element = processed_element
    except Exception as e:
        print(e)
        return e

    return element

async def extract_elements(url_list: List[str],
                           extract_func_list: List[Callable[[List[int], Page], List[Union[int, float]]]],
                           selectors_list: List[List[str]],
                           url_wait: Tuple[float, float] = [2, 5]) -> List[Union[List[float], float]]:
    """Extracts elements using specified extract function.
    """
    async with async_playwright() as p:
        # Open and go to URL
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        elements = []

        for i, url in enumerate(url_list):
            # If the URL times out, append the TimeoutError object
            try:
                await page.goto(url)
            except Exception as e:
                elements.append(e)
                continue # no need to asyncio.sleep since program took long
            
            print(f"Scraping {url}...")
            el = await extract_func_list[i](selectors_list[i], page)
            elements.append(el)
            wait_time = random.uniform(url_wait[0], url_wait[1])
            await asyncio.sleep(wait_time)

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

def update_db_entries(prices_url_list: List[str],
                      cached_db: dict,
                      file_path: str,
                      price_elements_list: List[List[float]] = None,
                      volume_elements_list: List[List[float]] = None,
                      mint_amt_element: int = 1,
                      price_array_len: int = PRICE_ARRAY_LEN) -> None:
    """Update database and return updated entries.
    """
    # Load price db
    # entries = read_json(file_path)
    entries = cached_db

    for i, url in enumerate(prices_url_list):
        # Extract standardized name and standardized url
        rune_name_standardized = rune_name_standardizer(prices_url_to_ticker(url))
        rune_url_standardized = rune_name_std_to_prices_url(rune_name_standardized)

        # Configure variables to store in db
        curr_time = datetime.now().strftime("%I:%M:%S %p, %m/%d/%Y")

        # Update prices, volume, and timestamps
        try:
            price_array = entries[rune_name_standardized]['price_array']
        except:
            price_array = []
        try:
            price_timestamps = entries[rune_name_standardized]['price_timestamps']
        except:
            price_timestamps = []
        try:
            mint_amt_element = entries[rune_name_standardized]['tokens_per_mint']
        except:
            mint_amt_element = mint_amt_element

        # Sometimes, a 'TimeoutError' object is assigned within price_elements_list.
        # If this happens, duplicate the previous value.
        try:
            volume = volume_elements_list[i]
        except TypeError:
            try:
                volume = entries[rune_name_standardized]['volume']
            except:
                volume = 0
        
        # Resolve edge case of first scraped element being a list
        price = price_elements_list[i]
        price = price[0] if type(price) is list else price

        # Sometimes, type 'type' gets scraped so copy last sample
        price = price if isinstance(price, numbers.Number) else price_array[-1]
        
        try:
            price_array.append(price)
        except TypeError:
            price_array.append(price_array[-1] + 0.000000001)

        price_timestamps.append(curr_time)
        if len(price_array) > price_array_len:
            price_array.pop(0)
            price_timestamps.pop(0)
        try:
            last_notified = entries[rune_name_standardized]['last_notified']
        except:
            last_notified = -1 # holder value that should never be in the checked array

        to_add = {
            'last_updated': curr_time,
            rune_name_standardized: {
                'url': rune_url_standardized,
                'tokens_per_mint': mint_amt_element, # TODO: replace the 0
                'price_array': price_array,
                'price_timestamps': price_timestamps,
                'last_notified': last_notified,
                'volume': volume
            }
        }

        entries.update(to_add) # update dictionary

    try:
        write_json("external_cache.json", entries)
    except:
        return entries
    
    write_json(file_path, entries)

    return entries



