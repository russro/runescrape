import re

from playwright.sync_api import sync_playwright
from typing import List


def save_element(element):
    pass

def extract_price_elements(url: str, elements_per_page: int, selectors: List[str]):
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
            element_text = float(re.sub("[^0-9.]", "", page.inner_text(selector))) # extract to float
            print("Element text:", element_text)
            print(type(element_text))

            elements[i] = element_text # Assign in ascending order

        browser.close()

