# Main file to run

import os
import discord
import random
from dotenv import load_dotenv
from pprint import pprint

def parse_recommendation(message):
    if not message.startsWith("!add "):
        return False
    else:
        return message.split("!add ")[1]

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    guild = discord.utils.get(client.guilds, name=GUILD)
    print(guild)

# When user sends a message to the channel
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if parse_recommendation(message.content):
        book_name = 
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    if message.content == '99!':
        response = random.choice(brooklyn_99_quotes)
        await message.channel.send(response)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()
client.run(TOKEN)