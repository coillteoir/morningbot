import bot


def main():
    with open("token", "r") as file:
        token = file.read()
        bot.client.run(token)


if __name__ == "__main__":
    main()
