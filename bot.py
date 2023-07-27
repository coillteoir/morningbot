#!/bin/python3

import time
import random
import json
from typing import Final

import discord
from discord.ext import tasks, commands

import requests
from datetime import date, timedelta

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)





def getWeather():
    # Get weather, using weatherapi.com
    key = "REPLACE WITH weatherapi.com KEY"
    response = requests.get(f"http://api.weatherapi.com/v1/forecast.json?key={key}&q=Dublin&days=1&aqi=no&alerts=no")
    data = response.json()
    forecast = data["forecast"]["forecastday"][0]
    max_temp_celsius = forecast["day"]["maxtemp_c"]
    min_temp_celsius = forecast["day"]["mintemp_c"]
    conditions = forecast["day"]["condition"]["text"]
    weather_icon_URL = forecast["day"]["condition"]["icon"]

    return max_temp_celsius, min_temp_celsius, conditions, weather_icon_URL

def getNews():
    # Get news, using newsapi.org
    key = "REPLACE WITH newsapi.org KEY"
    # response = requests.get(f"https://newsapi.org/v2/top-headlines?country=ie&apiKey={key}") NORMAL NEWS
    #https://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey={key} Tech crunch, maybe better headlines idk. Hopefully sorting by popularity will filter the clickbaity viagra articles
    response = requests.get(f"https://newsapi.org/v2/top-headlines?category=technology&sortBy=popularity&apiKey={key}") # TECH NEWS
    data = response.json()
    articles = data["articles"]
    headline_one = articles[0]["title"]
    headline_two = articles[1]["title"]
    headline_three = articles[2]["title"]

    return headline_one, headline_two, headline_three


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


with open('config/configuration_data.json') as f:
    configuration_data: Final[dict[str, list[str] | dict[str, str] | str | int]] = json.loads(f.read())

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    send_message.start()
    

@client.event
async def on_message(message):
    if message.author == client.user:
        await message.add_reaction("☀️")
        return
    contents = message.content.casefold()

    if time.localtime().tm_hour >= 6 and time.localtime().tm_hour <= 12:
        if "bad morning" in contents:
                print("bad morning detected")
                await message.add_reaction("🤬")
                return

        if any(element in contents for element in configuration_data["good_morning_phrases"]):
                print(f"gm detected > \"{message.content}\" by {message.author}")
                await message.add_reaction("☀️")
                return
    for egg_phrase in configuration_data["easter_egg_phrases"].keys():
        if egg_phrase in contents:
            await message.add_reaction(configuration_data["easter_egg_phrases"][egg_phrase])
    

# CALL EVERY HOUR
@tasks.loop(hours=1)
async def send_message():
    print(time.localtime().tm_hour)
    if time.localtime().tm_hour == 6:
        
        weatherData = getWeather()
        newsData = getNews()

        channel = client.get_channel(configuration_data["channel_id"])
        print(channel)
        embed=discord.Embed(title="Good Morning," + configuration_data["server_name"] + "!",
                                description=f"**Todays weather in Dublin:**\n{weatherData[2]}\nmin: {weatherData[1]}c\nmax: {weatherData[0]}c\n\n**Todays News:**\n{newsData[0]}\n\n{newsData[1]}\n\n{newsData[2]}\n\n**Have a great day!**", 
                                color=0x00ff00)
        embed.set_thumbnail(url=F"https:{weatherData[3]}")
        embed.set_image(url=random.choice(configuration_data["good_morning_gif_urls"]))
        await channel.send(embed=embed)
