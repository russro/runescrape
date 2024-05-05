
import os
import requests
import discord
import asyncio
import nest_asyncio
import validators
import runescrape

from discord.ext import commands


nest_asyncio.apply()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
access_token = os.getenv('DISCORD_TOKEN')


@bot.command()
async def add(ctx, rune_name_or_url):
    rune_name = runescrape.url_to_ticker(rune_name_or_url) if validators.url(rune_name_or_url) else rune_name_or_url
    rune_name_standardized = runescrape.rune_string_standardizer(rune_name)
    ... # check db
    ... # if rune exists in db, say so and return the last updated entry
    ... # if rune does not exist in db, scrape
    ... # if scrape fails, say so and return
    ... # if scrape succeeds, add to db and return the updated entry

def call_prices(url: str):
    """Scrapes prices from UniSat URL; returns prices for tokens without updating db.
    """
    price_elements = asyncio.run(runescrape.extract_price_elements(url)) # scrape price data at time
    curr_entries = runescrape.read_curr_entries(url, price_elements)

    return curr_entries

def call_save_prices(url: str):
    """Scrapes prices from UniSat URL; updates db and returns prices for tokens.
    """
    price_elements = asyncio.run(runescrape.extract_price_elements(url)) # scrape price data at time
    updated_entries = runescrape.update_db_entries(url, price_elements) # update database

    return updated_entries

def sats_to_usd(sats):
    """Convert sats to USD.
    """
    response = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
    sats_to_usd_rate = response.json()['bpi']['USD']['rate_float'] / 100000000
    return round(sats * sats_to_usd_rate, 2)

def scrape_disc_msg(url, entry):
    """Turn singular entry into a Discord-readable message.
    """
    ticker = runescrape.url_to_ticker(url)
    lowest_sats = entry[ticker]['curr_lowest_price']
    discmsg = (f"**{ticker}** is currently priced at **{lowest_sats} sats** per token"
               f" or **${sats_to_usd(lowest_sats)} USD** per token.")

    return discmsg

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!scrape'):
        url = message.content.replace('!scrape','').replace(' ','') # parse args from Discord message
        if validators.url(url):
            await message.channel.send('Scraping... Please wait.')
            curr_entries = call_prices(url)
            await message.channel.send(scrape_disc_msg(url, curr_entries))
        else:
            await message.channel.send("Input must be of form '!scrape [URL]'.")


if __name__ == "__main__":
    client.run(access_token)
