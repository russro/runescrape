
import os
import random
import requests
import bot
import asyncio
import nest_asyncio
import discord
import runescrape

from discord.ext import commands, tasks
from runescrape import PRICE_SELECTOR_LIST, MINT_AMOUNT_SELECTOR_LIST, PRICE_ARRAY_LEN
from listen import listen

listen()

# Config variables
PRICE_DATABASE_PATH = os.getenv('PRICE_DATABASE_PATH')
NICKNAME_DATABASE_PATH = os.getenv('NICKNAME_DATABASE_PATH')
BOT_CHANNEL_ID = 1232761629549265006
PERCENT_THRESHOLD = 10

# Global variables
try:
    PRICE_MVMT_LAST_CHECKED = runescrape.read_json(PRICE_DATABASE_PATH)['last_updated']
except:
    PRICE_MVMT_LAST_CHECKED = "04:20:69 PM, 04/20/2000"

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
    runescrape.update_db_entries(prices_url_list=[prices_url],
                                 file_path=PRICE_DATABASE_PATH,
                                 price_elements_list=[prices],
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

def rune_status_msg(curr_price_sats, curr_price_usd, tokens_per_mint) -> str:
    """Generate message to send for rune status.
    """
    msg = (f"{curr_price_sats} sats per token\n**${round(curr_price_usd, 6)}** per token\n"
           f"**${round(tokens_per_mint*curr_price_usd, 2)}** per mint ({tokens_per_mint} tokens per mint)\n\n")
    return msg

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
        msg = f"# Runes Prices\n**Last updated: {entries['last_updated']}** (updates every ~5 mins)\n\n"

        # Loop through db and construct msg iteratively
        for rune_name_std, rune_data in entries.items():
            # Skip 'last_updated'
            if rune_name_std == 'last_updated':
                continue
            
            # Configure vars to print
            ticker = runescrape.rune_name_std_to_ticker(rune_name_std)
            curr_price_sats = rune_data['price_array'][-1]
            curr_price_usd = sats_to_usd(curr_price_sats)
            tokens_per_mint = int(rune_data['tokens_per_mint'])

            # Construct and add to msg
            sub_msg = f"__{ticker}__:\n{rune_status_msg(curr_price_sats, curr_price_usd, tokens_per_mint)}"
            msg += sub_msg

        await ctx.send(msg)
        return
    else:
        # Check for nickname
        rune_potential_nickname = runescrape.rune_name_or_url_standardizer(rune_name_or_url)
        rune_name_standardized = rune_nickname_check_to_std(rune_potential_nickname)

        # Configure vars to print
        ticker = runescrape.rune_name_std_to_ticker(rune_name_standardized)
        curr_price_sats = entries[rune_name_standardized]['price_array'][-1]
        curr_price_usd = sats_to_usd(curr_price_sats)
        tokens_per_mint = int(entries[rune_name_standardized]['tokens_per_mint'])

        # Construct msg to send
        msg = f"**Last updated: {entries[rune_name_standardized]['price_timestamps'][-1]}** (updates every ~5 mins)\n\n"
        msg += f"__{ticker}__:\n{rune_status_msg(curr_price_sats, curr_price_usd, tokens_per_mint)}"
        
        await ctx.send(msg)
        return
    
@tasks.loop(seconds=5*60+random.uniform(-30,30)) # Check every 5 mins +/- 30 s
async def schedule_update_db():
    entries = runescrape.read_json(PRICE_DATABASE_PATH) # load db

    # Configure vars
    rune_names = list(entries.keys())
    rune_names.remove('last_updated') # skip 'last_updated'
    rune_cnt = len(rune_names)
    url_list = [0]*len(rune_names)
    for i, name in enumerate(rune_names):
        url_list[i] = entries[name]['url']
    extract_func_list = [runescrape.extract_prices]*rune_cnt
    selectors_list = [PRICE_SELECTOR_LIST]*rune_cnt
    
    price_elements = asyncio.run(runescrape.extract_elements(url_list, extract_func_list, selectors_list))
    runescrape.update_db_entries(prices_url_list=url_list,
                                 file_path=PRICE_DATABASE_PATH,
                                 price_elements_list=price_elements)
    
    return

@schedule_update_db.before_loop
async def schedule_update_before():
    await bot.wait_until_ready()
    print("Database schedule update function ready.")

@tasks.loop(seconds=60)
async def schedule_price_mvmt_check():
    # Load db
    entries = runescrape.read_json(PRICE_DATABASE_PATH)

    # Declare global var from config var
    global PRICE_MVMT_LAST_CHECKED

    # Return if already checked
    if PRICE_MVMT_LAST_CHECKED == entries['last_updated']:
        return

    # Update time checked
    PRICE_MVMT_LAST_CHECKED = entries['last_updated']

    # Check all runes for significant price mvmts
    for rune_name, rune_data in entries.items():
        # Skip 'last_updated'
        if rune_name == 'last_updated':
            continue
        
        # Skip entries that have been updated within the hour
        try:
            last_notified = rune_data['last_notified']
        except:
            last_notified = -1 # holder value that should never be in the checked array
        if last_notified in rune_data['price_timestamps']:
            continue

        # Extract prices particular rune
        price_array = rune_data['price_array']

        # Skip if not enough data 
        if len(price_array) < PRICE_ARRAY_LEN:
            continue
        
        # Extract timestamps, ticker for particular rune
        timestamp_array = rune_data['price_timestamps']
        ticker = runescrape.rune_name_std_to_ticker(rune_name)

        # Check for larger than PERCENT_THRESHOLD change
        old_price_sats = price_array[0]
        curr_price_sats = price_array[-1]
        curr_price_usd = sats_to_usd(curr_price_sats)
        tokens_per_mint = int(rune_data['tokens_per_mint'])
        percent_change = ((curr_price_sats-old_price_sats)/old_price_sats)*100

        # Send message for respective direction change
        if percent_change > PERCENT_THRESHOLD:
            # Update db with last_notified to prevent overnotifying channel
            to_add = {'last_notified': timestamp_array[-1]}
            entries[rune_name].update(to_add)
            runescrape.write_json(PRICE_DATABASE_PATH, entries)

            # Send price change msg
            msg_channel = bot.get_channel(BOT_CHANNEL_ID)
            await msg_channel.send("# Price up! We're so back.\n"
                                   f"**__{ticker}__ is up {round(abs(percent_change),2)}%** within the last hour:\n"
                                   f"{rune_status_msg(curr_price_sats, curr_price_usd, tokens_per_mint)}"
                                   f"<@&{1237541939562287164}>\n\n")
            
        elif percent_change < -PERCENT_THRESHOLD:
            # Update db with last_notified to prevent overnotifying channel
            to_add = {'last_notified': timestamp_array[-1]}
            entries[rune_name].update(to_add)
            runescrape.write_json(PRICE_DATABASE_PATH, entries)

            # Send price change msg
            msg_channel = bot.get_channel(BOT_CHANNEL_ID)
            await msg_channel.send("# Price down. It's over... <:pepehands:1237539581532966992>\n"
                                   f"**__{ticker}__ is down {round(abs(percent_change),2)}%** within the last hour:\n"
                                   f"{rune_status_msg(curr_price_sats, curr_price_usd, tokens_per_mint)}"
                                   f"<@&{1237541939562287164}>\n\n")

    return

@schedule_price_mvmt_check.before_loop
async def schedule_mvmt_check_before():
    await bot.wait_until_ready()
    print("Price movement check function ready.")

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    schedule_update_db.start()
    await asyncio.sleep(5)
    schedule_price_mvmt_check.start()


if __name__ == "__main__":
    bot.run(access_token)
    
