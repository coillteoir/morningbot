#!/bin/python3

import time
import discord

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

gmGifs = [
    "https://media.giphy.com/media/hHifLbLhEloqfDwWs0/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYXVwbnE0aGxyN2lkcTZ6ZzZ4d2NlYm5ldmJnYmgyZG9lMjQ5OTI3NiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/hVTtBEjpy6hj0OQSFb/giphy.gif",
    "https://media.giphy.com/media/hHifLbLhEloqfDwWs0/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExa25ycGx1ZHlmejVudmJ3aG50aTZwenMycHdld2IzbjlzM2tkYW5yNSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/aohA4u5GPmSDjrxYYK/giphy.gif",
    "https://media.giphy.com/media/l1KVc1iCZzvpflG80/giphy.gif",
    "https://media.giphy.com/media/3iBnSbhSfSuebzcZvT/giphy.gif",
    "https://media.giphy.com/media/hUEtOkI8ntRtBLyMfb/giphy.gif",
    "https://media.giphy.com/media/TKXMVRt5uvV8OYErao/giphy.gif"
    "https://media.giphy.com/media/mxjzBpyu8DDLIcEKVC/giphy.gif",
    "https://tenor.com/view/доброе-утро-кофе-coffee-gif-15999509",
    "https://media.giphy.com/media/hHifLbLhEloqfDwWs0/giphy.gif",
    "https://tenor.com/view/早安-早上好-goodmorning-flowers-sunflowers-gif-21233714",
    "https://tenor.com/view/おはようございます-good-morning-morning-in-japanese-gif-4722997724943366125",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ2o4amxqNnhsd3E4amIzN2VhZmhoOWdmdGV0a2VubG44MjE4ZjVvayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/JSw3ivlumEKZWrxdwp/giphy.gif",
    "https://media.giphy.com/media/E3qMYDlq0YIb0qXFug/giphy.gif",
    "https://tenor.com/view/suprabhat-good-morning-holidays-good-morning-hindi-good-morning-good-morning-happy-sunday-gif-19862051",
    "https://giphy.com/clips/greetings-holiday-kwanzaa-5yBrQnoPsjLaCo80fy",
    "https://media.giphy.com/media/lckQGTmmQYdjnXerK2/giphy.gif",
    "https://tenor.com/view/good-morning-günaydın-gif-25596075",
    "https://media0.giphy.com/media/f66sq76KfkDCKoxYSV/giphy.gif",
    "https://i.pinimg.com/originals/16/27/71/162771b373fc94042ec3e0e3615c0db1.gif",
    "https://tenor.com/view/good-morning-gif-25798053",
    "https://tenor.com/view/good-morning-gif-25798053"
    ]


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    

@client.event
async def on_message(message):
    if message.author == client.user:
        await message.add_reaction("☀️")
        return
    string = message.content.casefold()

    if time.localtime().tm_hour >= 6 and time.localtime().tm_hour <= 12:
        if "bad morning" in string:
            print("bad morning detected")
            await message.add_reaction("🤬")
            return

        if any(element in string for element in good_mornings):
            print(f"gm detected > \"{message.content}\" by {message.author}")
            await message.add_reaction("☀️")

            matched_index = next((index for index, element in enumerate(good_mornings) if element in string), None)
            print(f"Matched element position: {matched_index}")

            await message.channel.send(f"Good morning, {message.author.mention}! \n {gmGifs[matched_index]}")
            return
