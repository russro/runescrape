

import os
import discord
import asyncio
import nest_asyncio
import scrape

from playwright.async_api import async_playwright
from typing import List


# TODO: put into JSON file
URL = r"https://unisat.io/runes/market?tick=DOG%E2%80%A2GO%E2%80%A2TO%E2%80%A2THE%E2%80%A2MOON"
ELEMENTS_PER_PAGE = 20
SELECTORS = [
    f"#rc-tabs-0-panel-1 > div > div.trade-list > div:nth-child({x+1}) > div.content.display-domain.white > div.price-line > span.price"
    for x in range(ELEMENTS_PER_PAGE)
]

nest_asyncio.apply()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

access_token = os.getenv('DISCORD_TOKEN')


@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

def call_prices(url: str, selectors: List[str], elements_per_page: int):
    """Scrapes prices from Unisat URL; updates and returns prices for tokens.
    """
    price_elements = asyncio.run(scrape.extract_price_elements(url, selectors, elements_per_page)) # scrape price data at time
    updated_entries = scrape.update_db_entries(url, price_elements) # update database

    return updated_entries

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '!scrape':
        await message.channel.send('Scraping...')
        curr_entries = call_prices(URL, SELECTORS, ELEMENTS_PER_PAGE)
        await message.channel.send(curr_entries)


if __name__ == "__main__":
    # entries = call_prices(URL, SELECTORS, ELEMENTS_PER_PAGE)
    # print(entries)
    client.run(access_token)
