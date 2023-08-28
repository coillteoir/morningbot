import bot


def main():
    with open("token", "r", encoding="utf-8") as token_pointer:
        token = token_pointer.read()
        bot.client.run(token)


if __name__ == "__main__":
    main()
