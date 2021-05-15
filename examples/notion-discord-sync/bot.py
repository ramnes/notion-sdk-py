# Main file to run

import os
import discord
import random
from dotenv import load_dotenv
from pprint import pprint
import notion

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

def parse_recommendation(message):
    if not message.startswith("!add "):
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

    rec = parse_recommendation(message.content)
    if rec:
        print(rec)
        notion.add_recommendation(rec)
        # rec = look up rec in Google Books API
        encouraging_responses = [
            "Very exciting recommendation, I've added this!",
            "Woohoo, I've added this to the list :)",
            "We value your contribution :D"
        ]
        response = random.choice(encouraging_responses)
        await message.reply(response, mention_author=False)

# client.run(TOKEN)
rec="hhhh"
notion.add_recommendation(rec)