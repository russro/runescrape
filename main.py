
import os
import scrape
import asyncio

from typing import Final
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response


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
        response: str = await get_response(user_message)
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

def main() -> None:
    asyncio.run(bot.start(token=TOKEN))


if __name__ == "__main__":

    main()

    # entries = call_prices(URL, SELECTORS, ELEMENTS_PER_PAGE)
    # print(entries)
