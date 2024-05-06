
import os
import json
import re
import validators
import asyncio

from playwright.async_api import async_playwright
from typing import List, Callable
from datetime import datetime

PRICE_DATABASE_PATH = os.getenv('PRICE_DATABASE_PATH')
NICKNAME_DATABASE_PATH = os.getenv('NICKNAME_DATABASE_PATH')
ELEMENTS_PER_PAGE = 10
SELECTORS = [
    f"#rc-tabs-0-panel-1 > div > div.trade-list > div:nth-child({x+1}) > div.content.display-domain.white > div.price-line > span.price"
    for x in range(ELEMENTS_PER_PAGE)
]

async def extract_elements() -> List[float]:
    """Extracts elements 
    """
    async with async_playwright() as p:
        # Open and go to URL
        browser = await p.chromium.launch()
        page = await browser.new_page()
        print(type(page))

asyncio.run(extract_elements())

