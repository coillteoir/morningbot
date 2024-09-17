"""Main file of morningbot, loads environment info and runs"""

import os

from dotenv import load_dotenv

import bot


def main():
    load_dotenv()
    bot.client.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
