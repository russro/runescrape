
import os
import requests
import discord
import asyncio
import nest_asyncio
import validators
import runescrape

from discord.ext import commands


# Config variables
PRICE_DATABASE_PATH = os.getenv('PRICE_DATABASE_PATH')
NICKNAME_DATABASE_PATH = os.getenv('NICKNAME_DATABASE_PATH')

# Enable nested asyncio calls
nest_asyncio.apply()

# Discord bot setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
access_token = os.getenv('DISCORD_TOKEN')


@bot.command()
async def add(ctx, rune_name_or_url: str = None) -> None:
    """Add rune to database.
    """
    # Return if command input lacks
    if rune_name_or_url is None:
        await ctx.send("Input must be of form '!add [RUNE_NAME_OR_URL]'.")
        return
    
    # Standardize rune name/url
    rune_name_standardized = runescrape.rune_name_or_url_standardizer(rune_name_or_url)

    # Load db
    rune_prices = runescrape.read_json(file_path=PRICE_DATABASE_PATH)

    # Check db if rune already exists; if so, return
    if rune_name_standardized in rune_prices:
        await ctx.send(f"{rune_name_standardized} already added.")
        ... # TODO: send last updated entry
        return
    
    # Scrape web for rune
    url = runescrape.rune_name_standardized_to_url(rune_name_standardized)
    price_elements = runescrape.extract_price_elements(url)
    if isinstance(price_elements, Exception):
        await ctx.send("Rune either lacks enough entries or does not exist on UniSat.")
        return
    
    # Add scraped data to db
    
    

    ... # if scrape fails, say so and send
    ... # if scrape succeeds, add to db and send the updated entry

@bot.command()
async def status(ctx, rune_name_or_url: str = None):
    if rune_name_or_url is None:
        ...
        return
    else:
        rune_name_standardized = runescrape.rune_name_or_url_standardizer(rune_name_or_url)
        ... # open db
        ... # send 
        return


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

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
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
    bot.run(access_token)
