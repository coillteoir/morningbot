import bot
import sys

token = open("token", "r")

if __name__ == "__main__":
    bot.client.run(token.read()) 
    token.close()