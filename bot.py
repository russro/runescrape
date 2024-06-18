
import os
import random
import requests
import bot
import asyncio
import nest_asyncio
import discord
import numbers
import runescrape

from dotenv import load_dotenv
from discord.ext import commands, tasks
from sats_to_usd import sats_to_usd
from runescrape import PRICE_SELECTOR_LIST, PRICE_VOLUME_SELECTOR_LIST, MINT_AMOUNT_SELECTOR_LIST
from runescrape import PRICE_ARRAY_LEN
from sheets import init_worksheet_and_runes, construct_runes_corresponding_prices, update_worksheet
from sheets import SHEETS_URL

load_dotenv()

# Config variables
PRICE_DATABASE_PATH = os.getenv('PRICE_DATABASE_PATH')
NICKNAME_DATABASE_PATH = os.getenv('NICKNAME_DATABASE_PATH')
BOT_CHANNEL_ID = 1232761629549265006
PERCENT_THRESHOLD = 7.5

# Global variables
try:
    RUNES_DB = runescrape.read_json(PRICE_DATABASE_PATH)
    PRICE_MVMT_LAST_CHECKED = RUNES_DB['last_updated']
except:
    RUNES_DB = {}
    PRICE_MVMT_LAST_CHECKED = "04:20:69 PM, 04/20/2000"
try:
    NICKNAMES_DB = runescrape.read_json(NICKNAME_DATABASE_PATH)
except:
    NICKNAMES_DB = {}

# Enable nested asyncio calls
nest_asyncio.apply()

# Discord bot setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
access_token = os.getenv('DISCORD_TOKEN')
lock = asyncio.Lock()


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
    # rune_prices = runescrape.read_json(file_path=PRICE_DATABASE_PATH)
    async with lock:
        global RUNES_DB

        # Check db if rune already exists; if so, return
        if rune_name_standardized in RUNES_DB:
            await ctx.send(f"**{ticker}** already added.")
            ... # TODO: send last updated entry
            return
    
    # Scrape web for rune; if rune scrape fails, return
    prices_url = runescrape.rune_name_std_to_prices_url(rune_name_standardized)
    await ctx.send(prices_url)
    mint_amt_url = runescrape.rune_name_std_to_mint_amt_url(rune_name_standardized)

    price_extractor, mint_amt_extractor = runescrape.extract_prices_or_volume, runescrape.extract_mint_amount
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
    async with lock:
        RUNES_DB = runescrape.update_db_entries(prices_url_list=[prices_url],
                                                cached_db=RUNES_DB,
                                                file_path=PRICE_DATABASE_PATH,
                                                price_elements_list=[prices],
                                                mint_amt_element=mint_amt)

    await ctx.send(f"**{ticker}** added!")

    return

@bot.command()
async def mintcnt(ctx, rune_name_or_url: str = None, mint_amt: int = 1) -> None:
    await ctx.send("Adding mint amount to rune...")

    rune_name_standardized = runescrape.rune_name_or_url_standardizer(rune_name_or_url)

    async with lock:
        global RUNES_DB
        RUNES_DB[rune_name_standardized]['tokens_per_mint'] = mint_amt

    return

async def rune_nickname_check_to_std(potential_nickname: str) -> str:
    """Check for nickname and replace to standard rune name.
    """
    async with lock:
        global NICKNAMES_DB

        try:
            rune_name_standardized = NICKNAMES_DB[potential_nickname]
        except Exception as e:
            return e
        
        return rune_name_standardized

@bot.command()
async def nickname(ctx, rune_name_or_url: str, rune_nickname: str):
    """Add nickname to existing rune.
    """
    # Check db for rune
    rune_name_standardized = runescrape.rune_name_or_url_standardizer(rune_name_or_url)
    ticker = runescrape.rune_name_std_to_ticker(rune_name_standardized)

    async with lock:
        global RUNES_DB
        
        if rune_name_standardized not in RUNES_DB:
            await ctx.send(f"**{ticker}** not found in database.\n\n"
                        "Please input `!add [RUNE_NAME_OR_URL]` to add runes to the database.")
            return

        # Add nickname to nicknames db
        # nickname_db = runescrape.read_json(NICKNAME_DATABASE_PATH)
        global NICKNAMES_DB
        NICKNAMES_DB.update({rune_nickname: rune_name_standardized})
        runescrape.write_json(NICKNAME_DATABASE_PATH, NICKNAMES_DB)
        
        await ctx.send(f"**{ticker}** can now be referred as '{rune_nickname}'.")

        return

def rune_status_msg(curr_price_sats, curr_price_usd, tokens_per_mint, volume) -> str:
    """Generate message to send for rune status.
    """
    msg = (f"**{volume} BTC** volume (24h)\n"
           f"**{curr_price_sats} sats** per token\n**${round(curr_price_usd, 6)}** per token\n"
           f"**${round(tokens_per_mint*curr_price_usd, 2)}** per mint ({tokens_per_mint} tokens per mint)\n\n")
    return msg

@bot.command()
async def status(ctx, rune_name_or_url: str = None):
    async with lock:
        # entries = runescrape.read_json(PRICE_DATABASE_PATH)
        global RUNES_DB

        if not RUNES_DB:
            await ctx.send("Database is empty!\n\n"
                        "Please input `!add [RUNE_NAME_OR_URL]` to add runes to the database.")
            return

        if rune_name_or_url is None:

            # Configure header of msg
            msg = f"# Runes Prices\n**Last updated: {RUNES_DB['last_updated']}** (updates every ~5 mins)\n\n"

            # Loop through db and construct msg iteratively
            for rune_name_std, rune_data in RUNES_DB.items():
                # Skip 'last_updated'
                if rune_name_std == 'last_updated':
                    continue
                
                # Configure vars to print
                ticker = runescrape.rune_name_std_to_ticker(rune_name_std)
                curr_price_sats = rune_data['price_array'][-1]
                curr_price_usd = sats_to_usd(curr_price_sats)
                tokens_per_mint = int(rune_data['tokens_per_mint'])
                volume = rune_data['volume']

                # Construct and add to msg
                sub_msg = (f"__{ticker}__:\n"
                        f"{rune_status_msg(curr_price_sats, curr_price_usd, tokens_per_mint, volume)}")
                msg += sub_msg

            await ctx.send(msg)
            return
        else:
            # Check for nickname
            rune_potential_nickname = runescrape.rune_name_or_url_standardizer(rune_name_or_url)
            rune_name_standardized = rune_nickname_check_to_std(rune_potential_nickname)
            if isinstance(rune_name_standardized, Exception):
                await ctx.send('Nickname does not exist.')
                return

            # Configure vars to print
            ticker = runescrape.rune_name_std_to_ticker(rune_name_standardized)
            curr_price_sats = RUNES_DB[rune_name_standardized]['price_array'][-1]
            curr_price_usd = sats_to_usd(curr_price_sats)
            tokens_per_mint = int(RUNES_DB[rune_name_standardized]['tokens_per_mint'])
            volume = RUNES_DB[rune_name_standardized]['volume']

            # Construct msg to send
            msg = f"**Last updated: {RUNES_DB[rune_name_standardized]['price_timestamps'][-1]}** (updates every ~5 mins)\n\n"
            msg += f"__{ticker}__:\n{rune_status_msg(curr_price_sats, curr_price_usd, tokens_per_mint, volume)}"
            
            await ctx.send(msg)
            return

@tasks.loop(seconds=5*60)
async def db_check():
    """Check if db have been corrupted and retrieve a backup if so.
    """
    async with lock:
        global RUNES_DB
        global PRICE_DATABASE_PATH

        # If db is empty but the backup is filled, reupdate RUNES_DB
        if bool(RUNES_DB) is False and bool(runescrape.read_json(PRICE_DATABASE_PATH)) is True:
            RUNES_DB = runescrape.read_json(PRICE_DATABASE_PATH)

        return

# @tasks.loop(seconds=5*60)
async def schedule_price_mvmt_check():
    # Load db
    # entries = runescrape.read_json(PRICE_DATABASE_PATH)
    global RUNES_DB

    # Declare global var from config var
    global PRICE_MVMT_LAST_CHECKED

    # Skip if not updated
    try:
        RUNES_DB['last_updated']
    except KeyError:
        return

    # Return if already checked
    if PRICE_MVMT_LAST_CHECKED == RUNES_DB['last_updated']:
        return

    # Update time checked
    PRICE_MVMT_LAST_CHECKED = RUNES_DB['last_updated']

    print("Checking for price movements...")

    # Check all runes for significant price mvmts
    for rune_name, rune_data in RUNES_DB.items():
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
        volume = rune_data['volume']

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
            RUNES_DB[rune_name].update(to_add)
            runescrape.write_json(PRICE_DATABASE_PATH, RUNES_DB)

            # Send price change msg
            msg_channel = bot.get_channel(BOT_CHANNEL_ID)
            await msg_channel.send("# Price up! We're so back.\n"
                                   f"**__{ticker}__ is up {round(abs(percent_change),2)}%** within the last hour:\n"
                                   f"{rune_status_msg(curr_price_sats, curr_price_usd, tokens_per_mint, volume)}"
                                   f"<@&{1237541939562287164}>\n\n")
            
        elif percent_change < -PERCENT_THRESHOLD:
            # Update db with last_notified to prevent overnotifying channel
            to_add = {'last_notified': timestamp_array[-1]}
            RUNES_DB[rune_name].update(to_add)
            # runescrape.write_json(PRICE_DATABASE_PATH, RUNES_DB) # no need to write to db

            # Send price change msg
            msg_channel = bot.get_channel(BOT_CHANNEL_ID)
            await msg_channel.send("# Price down. It's over... <:pepehands:1237539581532966992>\n"
                                   f"**__{ticker}__ is down {round(abs(percent_change),2)}%** within the last hour:\n"
                                   f"{rune_status_msg(curr_price_sats, curr_price_usd, tokens_per_mint, volume)}"
                                   f"<@&{1237541939562287164}>\n\n")

    return

@tasks.loop(seconds=5*60+random.uniform(-30,30)) # Check every 5 mins +/- 30 s
async def schedule_update_db():
    # Check db corruption
    await db_check()
    
    async with lock:
        global RUNES_DB

        # Configure vars
        rune_names = list(RUNES_DB.keys())
        try:
            rune_names.remove('last_updated') # skip 'last_updated'
        except:
            pass
        url_list = [0]*len(rune_names)
        for i, name in enumerate(rune_names):
            url_list[i] = RUNES_DB[name]['url']
        rune_cnt = len(rune_names)
        extract_func_list = [runescrape.extract_prices_or_volume]*rune_cnt
        selectors_list = [PRICE_VOLUME_SELECTOR_LIST]*rune_cnt

    # Extract price and volume elements
    price_volume_elements = asyncio.run(runescrape.extract_elements(url_list, extract_func_list, selectors_list))
    price_elements, volume_elements = [], []
    for i, pair in enumerate(price_volume_elements):
        # Send message if scraped element is not a number
        if not isinstance(pair[0], numbers.Number):
            msg_channel = bot.get_channel(BOT_CHANNEL_ID)
            await msg_channel.send(f"WARNING: Scraped price_element {pair[0]} from {url_list[i]}./n"
                                   f"Appending previous price_element to current price.")
        if not isinstance(pair[1], numbers.Number):
            msg_channel = bot.get_channel(BOT_CHANNEL_ID)
            await msg_channel.send(f"WARNING: Scraped volume_element {pair[1]} from {url_list[i]}.\n"
                                   f"Setting volume_element as 0.")
        
        try:
            price_elements.append(pair[0])
            volume_elements.append(pair[1])
        except: # Append TimeoutError if the pair var is unsubscriptable
            price_elements.append(TimeoutError)
            volume_elements.append(TimeoutError)

    # Update cached db; skip if scrape fails
    async with lock:
        try:
            RUNES_DB = runescrape.update_db_entries(prices_url_list=url_list,
                                                    cached_db=RUNES_DB,
                                                    file_path=PRICE_DATABASE_PATH,
                                                    price_elements_list=price_elements,
                                                    volume_elements_list=volume_elements)
        except Exception as e:
            msg_channel = bot.get_channel(BOT_CHANNEL_ID)
            await msg_channel.send(e)
    
    # Check db again
    await db_check()

    # Check for price changes
    async with lock:
        await schedule_price_mvmt_check()

    # Update spreadsheet
    try:
        worksheet, rune_names_std = init_worksheet_and_runes(SHEETS_URL)
        runes_corresponding_prices = construct_runes_corresponding_prices(rune_names_std, RUNES_DB)
        print("Updating sheet...")
        update_worksheet(rune_names_std, worksheet, runes_corresponding_prices)
    except Exception as e:
        print(e)
    
    return

@schedule_update_db.before_loop
async def schedule_update_before():
    await bot.wait_until_ready()
    print("Database schedule update function ready.")

# @schedule_price_mvmt_check.before_loop
# async def schedule_mvmt_check_before():
#     await bot.wait_until_ready()
#     print("Price movement check function ready.")

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    schedule_update_db.start()
    # await asyncio.sleep(5)
    # schedule_price_mvmt_check.start()


if __name__ == "__main__":
    bot.run(access_token)
    
