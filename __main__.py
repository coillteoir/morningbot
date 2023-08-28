import bot


def main():
    with open("token", "r") as tp:
        token = tp.read()
        bot.client.run(token)


if __name__ == "__main__":
    main()
