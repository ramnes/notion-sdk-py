# Main file to run

import os
import logging
import discord
import random
from dotenv import load_dotenv
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

# When user sends a message to the channel
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    recommended_book = parse_recommendation(message.content)
    if recommended_book:
        print('Looking up your book recommendation!', recommended_book)
        success = notion.add_recommendation(recommended_book)
        if success:
            encouraging_responses = [
                "Very exciting recommendation, I've added this!",
                "Woohoo, I've added this to the list :)",
                "We value your contribution :D"
            ]
            response = random.choice(encouraging_responses)
            await message.reply(response, mention_author=False)
        else:
            response = "Oh no, looks like we couldn't update the list at this time ;_;"
            await message.reply(response, mention_author=False)

client.run(TOKEN)
