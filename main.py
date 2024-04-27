
import os
import scrape

from typing import List, Final
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response


URL = r"https://unisat.io/runes/market?tick=DOG%E2%80%A2GO%E2%80%A2TO%E2%80%A2THE%E2%80%A2MOON"
ELEMENTS_PER_PAGE = 20
SELECTORS = [
    f"#rc-tabs-0-panel-1 > div > div.trade-list > div:nth-child({x+1}) > div.content.display-domain.white > div.price-line > span.price"
    for x in range(ELEMENTS_PER_PAGE)
]


# LOAD TOKEN
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# BOT SETUP
intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

# MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled, probably.)')
        return
    
    if is_private := user_message[0] == '!':
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

# BOT STARTUP
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')

# HANDLING INCOMING MESSAGES
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return
    
    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    await send_message(message, user_message)

def call_prices(url: str, selectors: List[str], elements_per_page: int):
    """Scrapes prices from Unisat URL; updates and returns prices for tokens.
    """
    price_elements = scrape.extract_price_elements(url, selectors, elements_per_page) # scrape price data at time
    updated_entries = scrape.update_db_entries(url, price_elements) # update database

    return updated_entries

def main() -> None:
    client.run(token=TOKEN)


if __name__ == "__main__":

    main()

    # entries = call_prices(URL, SELECTORS, ELEMENTS_PER_PAGE)
    # print(entries)
