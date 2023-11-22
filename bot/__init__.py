#!/bin/python3

import json
import random
import signal
import sys
import time
from datetime import date, datetime, timedelta
import re

import discord
import pytz
import requests
from discord.ext import commands, tasks

import leaderboard

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Get the configuration
with open("config/configuration_data.json", "r", encoding="utf-8") as config_file:
    configuration_data = json.loads(config_file.read())

TIMEZONE = pytz.timezone(configuration_data["timezone"])
MORNING_EMOJI = configuration_data["morning_emoji"]
EARLY_EMOJI = configuration_data["early_emoji"]
BAD_MORNING_EMOJI = configuration_data["bad_morning_emoji"]
SERVER_NAME = configuration_data["server_name"]
CHANNEL_ID = configuration_data["channel_id"]
MORNING_GIFS = configuration_data["good_morning_gif_urls"]
WEATHER_API_KEY = configuration_data["weather_api_key"]
NEWS_API_KEY = configuration_data["news_api_key"]
GOOD_MORNING_PHRASES = configuration_data["good_morning_phrases"]
DEBUG_MODE = configuration_data["debug_mode"]
DEBUG_TIME = 9  # debug line >1
DEBUG_MINUTE = "01:00"  # debug line >2

PATTERN = r"^passx debug_time = (\d+)$"
PATTERN2 = r"^passx debug_minute = (\d+:\d+)$"


def get_weather():
    # Get weather, using weatherapi.com
    response = requests.get(
        "http://api.weatherapi.com/v1/forecast.json?"
        + f"key={WEATHER_API_KEY}&q=Dublin&days=1&aqi=no&alerts=no",
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
        + f"Key={NEWS_API_KEY}",
        timeout=10,
    )  # TECH NEWS
    data = response.json()
    articles = data["articles"]
    headline_one = articles[0]["title"]
    headline_two = articles[1]["title"]
    headline_three = articles[2]["title"]

    return headline_one, headline_two, headline_three


def get_current_hour():
    if DEBUG_MODE:
        return DEBUG_TIME  # debug line >1
    return int(datetime.now(TIMEZONE).strftime("%H"))


def get_current_minute():
    if DEBUG_MODE:
        return DEBUG_MINUTE  # debug line >2
    return str(datetime.now(TIMEZONE).strftime("%H:%M"))


@client.event
async def on_ready():
    send_message.start()
    print(f"We have logged in as {client.user}, time is {get_current_hour()}")


server_leaders = leaderboard.Leaderboard(configuration_data["channel_id"])
FIRST_GM = False
FIRST_GM_USER = None


@client.event
async def on_message(message):
    global FIRST_GM
    global FIRST_GM_USER
    if message.author == client.user:
        await message.add_reaction(MORNING_EMOJI)
        return
    contents = message.content.casefold()

    if 6 <= get_current_hour() <= 12:
        if "bad morning" in contents:
            print("bad morning detected")
            await message.add_reaction(BAD_MORNING_EMOJI)
            return

        # Use regular expressions to check for good morning phrases small changes
        for pattern in GOOD_MORNING_PHRASES:
            if re.search(rf'\b{re.escape(pattern)}\b', contents):
                print(f'gm detected > "{message.content}" by {message.author}')
                if FIRST_GM is False:
                    FIRST_GM_USER = message.author
                    FIRST_GM = True

                    await message.add_reaction(EARLY_EMOJI)
                    server_leaders.add_point(message.author)
                    return

                server_leaders.add_point(message.author)
                await message.add_reaction(MORNING_EMOJI)

                return

    # Performing regular expression checking on easter egg phrases
    for egg_phrase, reaction in configuration_data["easter_egg_phrases"].items():
        if re.search(egg_phrase, contents):
            await message.add_reaction(reaction)
            return


    if DEBUG_MODE:
        if re.match(PATTERN, contents.lower()):  # debug block >1
            extracted_number = re.match(PATTERN, contents.lower()).group(1)
            global DEBUG_TIME
            DEBUG_TIME = int(extracted_number)
            print(f"debug time changed to {extracted_number}")
            await message.channel.send(f"debug time changed to {extracted_number}")

        if re.match(PATTERN2, contents.lower()):  # debug block >2
            extracted_number = re.match(PATTERN2, contents.lower()).group(1)
            global DEBUG_MINUTE
            DEBUG_MINUTE = extracted_number
            print(f"debug time changed to {extracted_number}")
            await message.channel.send(f"debug minute changed to {extracted_number}")


@tasks.loop(seconds=60)
async def send_message():
    global FIRST_GM
    global FIRST_GM_USER

    if get_current_minute() == "06:00":
        weather_data = get_weather()
        news_data = get_news()

        channel = client.get_channel(CHANNEL_ID)
        print(channel)
        embed = discord.Embed(
            title="Good Morning," + SERVER_NAME + "!",
            description=(
                "**Todays weather in Dublin:**\n"
                + f"{weather_data[2]}\n"
                + f"min: {weather_data[1]}c\n"
                + f"max: {weather_data[0]}c\n\n"
                + "**Todays News:**\n"
                + f"{news_data[0]}\n\n"
                + f"{news_data[1]}\n\n"
                + f"{news_data[2]}\n\n"
                + "**Have a great day!**"
            ),
            color=0x00FF00,
        )
        embed.set_thumbnail(url=f"https:{weather_data[3]}")
        embed.set_image(url=random.choice(MORNING_GIFS))
        await channel.send(embed=embed)

    if get_current_minute() == "13:00":
        # If theres no early bird, dont send the message
        if FIRST_GM is False:
            return
        temp_first = FIRST_GM_USER
        FIRST_GM = False
        FIRST_GM_USER = None

        channel = client.get_channel(CHANNEL_ID)
        embed = discord.Embed(
            title="Good Afternoon, " + SERVER_NAME + "!",
            description=(
                "Todays early bird was "
                + str(temp_first)
                + "!\n\n"
                + "Today's leaderboard is:"
                + str(server_leaders)
            ),
            color=0x00FF00,
        )
        embed.set_image(url=random.choice(MORNING_GIFS))
        await channel.send(embed=embed)

        # Reset early bird every day

        FIRST_GM = False
        FIRST_GM_USER = None


def sighandle_exit(sig, frame):
    print(sig, frame)
    print("Exiting using handler")
    server_leaders.dump_data()
    sys.exit()


signal.signal(signal.SIGINT, sighandle_exit)
signal.signal(signal.SIGTERM, sighandle_exit)
