import bot


def main():
    tp = open("token", "r")
    token = tp.read()
    tp.close()
    bot.client.run(token)


if __name__ == "__main__":
    main()
