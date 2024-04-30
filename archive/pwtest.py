
import os
import discord
import asyncio
import nest_asyncio
nest_asyncio.apply()

from playwright.async_api import async_playwright

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

access_token = os.getenv('DISCORD_TOKEN')

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

async def scrape_(message):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://unisat.io/')
        title = await page.title()
        await message.channel.send(f'The page title is: {title}')
        await browser.close()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '!scrape':
        await message.channel.send('Scraping...')
        asyncio.run(scrape_(message))

client.run(access_token)
