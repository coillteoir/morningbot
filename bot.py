#!/bin/python3

import time
import discord
from leaderboard import LeaderBoard

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

good_mornings = [
    "good morning",
    "maidin mhaith",
    "gm",
    "buenos días",
    "bonjour",
    "guten morgen",
    "buongiorno",
    "bom dia",
    "goedemorgen",
    "доброе утро",
    "早上好",
    "おはようございます",
    "좋은 아침입니다",
    "صباح الخير",
    "सुप्रभात",
    "habari za asubuhi",
    "καλημέρα",
    "günaydın",
    "god morgon",
    "dzień dobry",
    "בוקר טוב",
    "สวัสดีตอนเช้า"
]


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    

@client.event
async def on_message(message):
    if message.author == client.user:
        await message.add_reaction("☀️")
        return
    string = message.content
    string = string.lower()
    if time.localtime().tm_hour >= 6 and time.localtime().tm_hour <= 23:
        if string == "bad morning":
            print("bad morning detected")
            await message.add_reaction("🤬")
            return

        for x in good_mornings:
            if string in x:
                print("gm detected", message.content)
                await message.add_reaction("☀️")
                return
