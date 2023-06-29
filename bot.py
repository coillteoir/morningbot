#!/bin/python3

import time
import discord
from discord.ext import tasks, commands
import requests
from datetime import date, timedelta, datetime

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


channel_id = 1053499749443059814



# Get weather, using weatherapi.com
key = "REPLACE WITH weatherapi.com KEY"
response = requests.get(f"http://api.weatherapi.com/v1/forecast.json?key={key}&q=Dublin&days=1&aqi=no&alerts=no")
data = response.json()
forecast = data["forecast"]["forecastday"][0]
max_temp_celsius = forecast["day"]["maxtemp_c"]
min_temp_celsius = forecast["day"]["mintemp_c"]
conditions = forecast["day"]["condition"]["text"]
weather_icon_URL = forecast["day"]["condition"]["icon"]


# Get news, using newsapi.org
key = "REPLACE WITH newsapi.org KEY"
# response = requests.get(f"https://newsapi.org/v2/top-headlines?country=ie&apiKey={key}") NORMAL NEWS
response = requests.get(f"https://newsapi.org/v2/top-headlines?country=ie&category=technology&apiKey={key}") # TECH NEWS
data = response.json()
articles = data["articles"]
headline_one = articles[0]["title"]
headline_two = articles[1]["title"]
headline_three = articles[2]["title"]


def getVideo():
    #Get fireship vids, using Youtube Data API v3
    key = "REPLACE WITH Youtube Data API v3 KEY"
    channel_ID = "UCsBjURrPoezykLs9EqgamOA"

    # Get today's date
    today = date.today()
    # Calculate yesterday's date
    yesterday = today - timedelta(days=1)

    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_ID}&type=video&order=date&maxResults=1&publishedAfter={yesterday}T23:00:00Z&key={key}"
    response = requests.get(url)
    data = response.json()
    try:
        video_title = data["items"][0]["snippet"]["title"]
    except:
        video_title = "No video today :("

    print(video_title)
    return video_title





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
    send_message.start()
    

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
                return


# CALL EVERY HOUR
@tasks.loop(hours=1)
async def send_message():
    print(time.localtime().tm_hour)
    if time.localtime().tm_hour == 6:
        channel = client.get_channel(channel_id)
        print(channel)
        embed=discord.Embed(title="Good Morning!", 
                                description=f"**Todays weather in Dublin:**\n{conditions}\nmin: {min_temp_celsius}c\nmax: {max_temp_celsius}c\n\n**Todays News:**\n{headline_one}\n\n{headline_two}\n\n{headline_three}\n\n**Fireship Videos:**\n{getVideo()}\n\n**Have a great day!**", 
                                color=0x00ff00)
        embed.set_thumbnail(url=F"https:{weather_icon_URL}")
        embed.set_image(url=gmGifs[0])
        await channel.send(embed=embed)