#!/usr/bin/env python3

import json
import random
import signal
import sys
import time
import os
import re
from datetime import date, datetime, timedelta

import discord
import pytz
import requests
from discord.ext import commands, tasks

from leaderboard import Leaderboard

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


class Bot():
    def __init__(self, path):
        config = None

        with open(path, "r", encoding="utf-8") as config_file:
            config = json.loads(config_file.read())

        if config is None:
            print("config could not be loaded", sys.stderr)
            return


        self.weather_api_key = os.getenv("WEATHER_API_KEY")
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.channel_id = os.getenv("MAIN_CHANNEL_ID")

        self.server_name = config["bot"]["server_name"]
        self.timezone = pytz.timezone(config["bot"]["timezone"])
        self.debug_mode = config["bot"]["debug_mode"]

        self.morning_emoji = config["morning"]["morning_emoji"]
        self.early_emoji = config["morning"]["early_emoji"]
        self.bad_morning_emoji = config["morning"]["bad_morning_emoji"]
        self.morning_gifs = config["morning"]["good_morning_gif_urls"]
        self.good_morning_phrases = config["morning"]["good_morning_phrases"]

        self.easter_egg_patterns = config["easter_egg_patterns"]
        self.first_gm = False
        self.first_gm_user = None
        self.debug_time = None

        self.pattern = r"^passx debug_time = (\d+)$"
        self.pattern2 = r"^passx debug_minute = (\d+:\d+)$"
        self.debug_time = 9  # debug line >1
        self.debug_minute = "01:00"  # debug line >2

        self.leaderboard = Leaderboard(self.channel_id)

bot = Bot("config/configuration_data.json")


def get_weather():
    # Get weather, using weatherapi.com
    response = requests.get(
        "http://api.weatherapi.com/v1/forecast.json?"
        + f"key={bot.weather_api_key}&q=Dublin&days=1&aqi=no&alerts=no",
        timeout=10,
    )
    data = response.json()
    forecast = data["forecast"]["forecastday"][0]
    max_temp_celsius = forecast["day"]["maxtemp_c"]
    min_temp_celsius = forecast["day"]["mintemp_c"]
    conditions = forecast["day"]["condition"]["text"]
    weather_icon_url = forecast["day"]["condition"]["icon"]

    return max_temp_celsius, min_temp_celsius, conditions, weather_icon_url


def get_news():
    response = requests.get(
        "https://newsapi.org/v2/top-headlines?category=technology&sortBy=popularity&api"
        + f"Key={bot.news_api_key}",
        timeout=10,
    )  # TECH NEWS
    data = response.json()
    articles = data["articles"]
    headline_one = articles[0]["title"]
    headline_two = articles[1]["title"]
    headline_three = articles[2]["title"]

    return headline_one, headline_two, headline_three


def get_current_hour():
    if bot.debug_mode:
        return bot.debug_time  # debug line >1
    return int(datetime.now(bot.timezone).strftime("%H"))


def get_current_minute():
    if bot.debug_mode:
        return bot.debug_minute  # debug line >2
    return str(datetime.now(bot.timezone).strftime("%H:%M"))


@client.event
async def on_ready():
    send_message.start()
    print(f"We have logged in as {client.user}, time is {get_current_hour()}")

@client.event
async def on_message(message):
    if message.author == client.user:
        await message.add_reaction(bot.morning_emoji)
        return
    contents = message.content.casefold()

    if 6 <= get_current_hour() <= 12:
        if "bad morning" in contents:
            print("bad morning detected")
            await message.add_reaction(bot.bad_morning_emoji)
            return

        # Use regular expressions to check for good morning phrases small changes
        for pattern in bot.good_morning_phrases:
            if re.search(rf"\b{re.escape(pattern)}\b", contents):
                print(f'gm detected > "{message.content}" by {message.author}')
                if bot.first_gm is False:
                    bot.first_gm_user = message.author
                    bot.first_gm = True

                    await message.add_reaction(bot.early_emoji)
                    bot.leaderboard.add_point(message.author)
                    return

                bot.leaderboard.add_point(message.author)
                await message.add_reaction(bot.morning_emoji)

                return

    # Performing regular expression checking on easter egg phrases
    for egg_phrase, reaction in bot.easter_egg_patterns.items():
        if re.search(egg_phrase, contents):
            await message.add_reaction(reaction)
            return

    if bot.debug_mode:
        if re.match(bot.pattern, contents.lower()):  # debug block >1
            extracted_number = re.match(bot.pattern, contents.lower()).group(1)
            bot.debug_time = int(extracted_number)
            print(f"debug time changed to {extracted_number}")
            await message.channel.send(f"debug time changed to {extracted_number}")

        if re.match(bot.pattern2, contents.lower()):  # debug block >2
            extracted_number = re.match(bot.pattern2, contents.lower()).group(1)
            bot.debug_minute = extracted_number
            print(f"debug time changed to {extracted_number}")
            await message.channel.send(f"debug minute changed to {extracted_number}")


async def morning_message():
    weather_data = get_weather()
    news_data = get_news()

    channel = client.get_channel(bot.channel_id)
    embed = discord.Embed(
        title=f"Good Morning, {bot.server_name}!",
        description=(
            f"**Todays weather:**\n \
            {weather_data[2]}\n \
            min: {weather_data[1]}c\n \
            max: {weather_data[0]}c\n\n \
            **Todays News:**\n \
            {news_data[0]}\n\n \
            {news_data[1]}\n\n \
            {news_data[2]}\n\n \
            **Have a great day!**"
        ),
        color=0x00FF00,
    )
    embed.set_thumbnail(url=f"https:{weather_data[3]}")
    embed.set_image(url=random.choice(bot.morning_gifs))
    await channel.send(embed=embed)


async def afternoon_message():
    # If theres no early bird, dont send the message
    if bot.first_gm is False:
        return
    temp_first = bot.first_gm_user
    bot.first_gm = False
    bot.first_gm_user = None

    channel = client.get_channel(bot.channel_id)
    embed = discord.Embed(
        title=f"Good Afternoon, {bot.server_name}!",
        description=(
            "Todays early bird was {temp_first}!\n\n \
            Leaderboard:{bot.leaderboard}"
        ),
        color=0x00FF00,
    )
    embed.set_image(url=random.choice(bot.morning_gifs))
    await channel.send(embed=embed)

    # Reset early bird every day

    bot.first_gm = False
    bot.first_gm_user = None


@tasks.loop(seconds=60)
async def send_message():
    if get_current_minute() == "06:00":
        await morning_message()

    if get_current_minute() == "13:00":
        await afternoon_message()


def sighandle_exit(sig, frame):
    print(sig, frame)
    print("Exiting using handler")
    bot.leaderboard.dump_data()
    sys.exit()


signal.signal(signal.SIGINT, sighandle_exit)
signal.signal(signal.SIGTERM, sighandle_exit)
