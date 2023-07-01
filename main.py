import bot
import sys

def main():
    token = open("token", "r")
    bot.client.run(token.read()) 
    token.close()

if __name__ == "__main__":
    main()