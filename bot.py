
import os
import time
import requests
import bot
import asyncio
import nest_asyncio
import discord
import runescrape

from discord.ext import commands
from runescrape import PRICE_SELECTOR_LIST, MINT_AMOUNT_SELECTOR_LIST


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
async def test(ctx, *,arg):
    """Discord test command.
    """
    await ctx.channel.send(arg)

@bot.command()
async def add(ctx, rune_name_or_url: str = None) -> None:
    """Add rune to database.
    """
    await ctx.send("Adding rune to database...")

    # Return if command input lacks
    if rune_name_or_url is None:
        await ctx.send("Input must be of form `!add [RUNE_NAME_OR_URL]`.")
        return
    
    # Standardize rune name/url
    rune_name_standardized = runescrape.rune_name_or_url_standardizer(rune_name_or_url)
    ticker = runescrape.rune_name_std_to_ticker(rune_name_standardized)

    # Load db
    rune_prices = runescrape.read_json(file_path=PRICE_DATABASE_PATH)

    # Check db if rune already exists; if so, return
    if rune_name_standardized in rune_prices:
        await ctx.send(f"**{ticker}** already added.")
        ... # TODO: send last updated entry
        return
    
    # Scrape web for rune; if rune scrape fails, return
    prices_url = runescrape.rune_name_std_to_prices_url(rune_name_standardized)
    await ctx.send(prices_url)
    mint_amt_url = runescrape.rune_name_std_to_mint_amt_url(rune_name_standardized)

    price_extractor, mint_amt_extractor = runescrape.extract_prices, runescrape.extract_mint_amount
    prices, mint_amt = asyncio.run(runescrape.extract_elements(
        url_list = [prices_url, mint_amt_url],
        extract_func_list = [price_extractor, mint_amt_extractor],
        selectors_list = [PRICE_SELECTOR_LIST, MINT_AMOUNT_SELECTOR_LIST]
        ))

    # If price scrape fails, return
    if isinstance(prices, Exception):
        await ctx.send("Rune either lacks enough entries or does not exist on UniSat.")
        return
    
    # If mint amt scrape fails, set to one
    if isinstance(mint_amt, Exception):
        mint_amt = 1

    # Add scraped data to db
    runescrape.update_db_entries(prices_url=prices_url,
                                 file_path=PRICE_DATABASE_PATH,
                                 price_elements=prices,
                                 mint_amt_element=mint_amt)

    await ctx.send(f"**{ticker}** added!")

    return

def sats_to_usd(sats):
    """Convert sats to USD.
    """
    response = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
    # time.sleep() # TODO: consider this if I am getting timed out
    sats_to_usd_rate = response.json()['bpi']['USD']['rate_float'] / 100000000
    # return round(sats * sats_to_usd_rate, 2)
    return sats * sats_to_usd_rate

def rune_nickname_check_to_std(potential_nickname: str) -> str:
    """Check for nickname and replace to standard rune name.
    """
    nicknames = runescrape.read_json(file_path=NICKNAME_DATABASE_PATH)
    try:
        if potential_nickname in nicknames:
            rune_name_standardized = nicknames[potential_nickname]
    except:
        rune_name_standardized = potential_nickname
    
    return rune_name_standardized

@bot.command()
async def nickname(ctx, rune_name_or_url: str, rune_nickname: str):
    """Add nickname to existing rune.
    """
    # Check db for rune
    rune_name_standardized = runescrape.rune_name_or_url_standardizer(rune_name_or_url)
    ticker = runescrape.rune_name_std_to_ticker(rune_name_standardized)
    entries = runescrape.read_json(PRICE_DATABASE_PATH)
    if rune_name_standardized not in entries:
        await ctx.send(f"**{ticker}** not found in database.\n\n"
                       "Please input `!add [RUNE_NAME_OR_URL]` to add runes to the database.")
        return

    # Add nickname to nicknames db
    nickname_db = runescrape.read_json(NICKNAME_DATABASE_PATH)
    nickname_db.update({rune_nickname: rune_name_standardized})
    runescrape.write_json(NICKNAME_DATABASE_PATH, nickname_db)
    
    await ctx.send(f"**{ticker}** can now be referred as '{rune_nickname}'.")

    return

@bot.command()
async def status(ctx, rune_name_or_url: str = None):
    entries = runescrape.read_json(PRICE_DATABASE_PATH)

    if not entries:
        await ctx.send("Database is empty!\n\n"
                       "Please input `!add [RUNE_NAME_OR_URL]` to add runes to the database.")
        return

    if rune_name_or_url is None:
        entries = runescrape.read_json(PRICE_DATABASE_PATH)

        # Configure header of msg
        msg = f"# Runes Prices\n**Last updated: {entries['last_updated']}**\n\n"

        # Loop through db and construct msg iteratively
        for rune_name_std, rune_data in entries.items():
            # Skip 'last_updated'
            if rune_name_std == 'last_updated':
                continue

            ticker = runescrape.rune_name_std_to_ticker(rune_name_std)
            curr_price_sats = rune_data['price_array'][-1]
            curr_price_usd = round(sats_to_usd(curr_price_sats), 4)
            tokens_per_mint = int(rune_data['tokens_per_mint'])
            sub_msg = (f"**{ticker}**: {curr_price_sats} sats or ${curr_price_usd} per token"
                       f" | ${round(tokens_per_mint*curr_price_usd, 2)} per {tokens_per_mint} tokens (tokens in a mint).\n\n")
            msg += sub_msg

        await ctx.send(msg)
        return
    else:
        rune_potential_nickname = runescrape.rune_name_or_url_standardizer(rune_name_or_url)
        rune_name_standardized = rune_nickname_check_to_std(rune_potential_nickname)
        ticker = runescrape.rune_name_std_to_ticker(rune_name_standardized)
        curr_price_sats = entries[rune_name_standardized]['price_array'][-1]
        curr_price_usd = round(sats_to_usd(curr_price_sats), 4)
        tokens_per_mint = int(entries[rune_name_standardized]['tokens_per_mint'])
        msg = (f"**Last updated: {entries[rune_name_standardized]['price_timestamps'][-1]}**\n\n"
               f"**{ticker}**: {curr_price_sats} sats or ${curr_price_usd} per token"
               f" | ${round(tokens_per_mint*curr_price_usd, 2)} per {tokens_per_mint} tokens (tokens in a mint).\n\n")
        
        await ctx.send(msg)
        return
    


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

# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return

#     if message.content.startswith('!scrape'):
#         url = message.content.replace('!scrape','').replace(' ','') # parse args from Discord message
#         if validators.url(url):
#             await message.channel.send('Scraping... Please wait.')
#             curr_entries = call_prices(url)
#             await message.channel.send(scrape_disc_msg(url, curr_entries))
#         else:
#             await message.channel.send("Input must be of form '!scrape [URL]'.")


if __name__ == "__main__":
    bot.run(access_token)
