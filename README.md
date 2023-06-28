# MorningBot

MorningBot is a Discord Bot built for CS++'s Discord Server. It reacts to all morning messages and has other fun features like leaderboards and hidden reacts.

## Installation & Deployment

When deploying, you may choose to deploy as a container, or deploy directly to your machine, any instruction that is Docker-only will be marked with a 🐳, direct deployment will be marked with a 🚀.

1. Clone the repository and install the dependencies.

```bash
git clone
pip install -r requirements.txt
```

2. Create a file called 'token' and put in your bot token.

3. 🚀 Run the bot.

```bash
python3 main.py
```

3. 🐳 Build the container.

```bash
docker build -t morningbot .
```

4. 🐳 Run the container.

```bash
docker run -d --name morningbot morningbot
```