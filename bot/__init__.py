#!/bin/python3

import json
import random
import time
from datetime import date, timedelta, datetime

import discord
import requests
from discord.ext import commands, tasks
import pytz

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


def get_weather():
    # Get weather, using weatherapi.com
    key = "REPLACE WITH weatherapi.com KEY"
    response = requests.get(
        f"http://api.weatherapi.com/v1/forecast.json?key={key}&q=Dublin&days=1&aqi=no&alerts=no",
        timeout=10
    )
    data = response.json()
    forecast = data["forecast"]["forecastday"][0]
    max_temp_celsius = forecast["day"]["maxtemp_c"]
    min_temp_celsius = forecast["day"]["mintemp_c"]
    conditions = forecast["day"]["condition"]["text"]
    weather_icon_url = forecast["day"]["condition"]["icon"]

    return max_temp_celsius, min_temp_celsius, conditions, weather_icon_url


def get_news():
    key = "REPLACE WITH newsapi.org KEY"
    response = requests.get(
        f"https://newsapi.org/v2/top-headlines?category=technology&sortBy=popularity&apiKey={key}",
        timeout=10
    )  # TECH NEWS
    data = response.json()
    articles = data["articles"]
    headline_one = articles[0]["title"]
    headline_two = articles[1]["title"]
    headline_three = articles[2]["title"]

    return headline_one, headline_two, headline_three


with open("config/configuration_data.json", "r", encoding="utf-8") as config_file:
    configuration_data = json.loads(config_file.read())

timezone = pytz.timezone(configuration_data["timezone"])

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    send_message.start()


@client.event
async def on_message(message):
    if message.author == client.user:
        await message.add_reaction("☀️")
        return
    contents = message.content.casefold()

    current_hour = int(datetime.now(timezone).strftime("%H"))
    if 6 <= current_hour <= 12:
        if "bad morning" in contents:
            print("bad morning detected")
            await message.add_reaction("🤬")
            return

        if any(
            element in contents
            for element in configuration_data["good_morning_phrases"]
        ):
            print(f'gm detected > "{message.content}" by {message.author}')
            await message.add_reaction("☀️")
            return
    for egg_phrase in configuration_data["easter_egg_phrases"].keys():
        if egg_phrase in contents:
            await message.add_reaction(
                configuration_data["easter_egg_phrases"][egg_phrase]
            )


# CALL EVERY HOUR
@tasks.loop(hours=1)
async def send_message():
    print(int(datetime.now(timezone).strftime("%H")))
    if int(datetime.now(timezone).strftime("%H")) == 6:
        weather_data = get_weather()
        news_data = get_news()

        channel = client.get_channel(configuration_data["channel_id"])
        print(channel)
        embed = discord.Embed(
            title="Good Morning," + configuration_data["server_name"] + "!",
            description=("**Todays weather in Dublin:**\n"+
                         f"{weather_data[2]}\n"+
                         f"min: {weather_data[1]}c\n"+
                         f"max: {weather_data[0]}c\n\n"+
                         "**Todays News:**\n"+
                         f"{news_data[0]}\n\n"+
                         f"{news_data[1]}\n\n"+
                         f"{news_data[2]}\n\n"+
                         "**Have a great day!**"),
            color=0x00FF00,
        )
        embed.set_thumbnail(url=f"https:{weather_data[3]}")
        embed.set_image(url=random.choice(configuration_data["good_morning_gif_urls"]))
        await channel.send(embed=embed)
        