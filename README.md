# MorningBot

MorningBot is a Discord Bot built for CS++'s Discord Server. It reacts to all morning messages and has other fun features like leaderboards and hidden reacts.

## Installation, Deployment and Development

When deploying, you may choose to deploy as a container, or deploy directly to your machine, any instruction that is Docker-only will be marked with a 🐳, direct deployment only will be marked with a 🚀.

### Installation
1. Clone the repository
```bash
git clone https://github.com/davidlynch-sd/MorningBot
```

2. 🚀 Install the dependencies.
```bash
pip install -r requirements.txt
```

### Deployment and Development

3. Create a file called 'token' and put in your bot token.

4. 🚀 Run the bot.

```bash
python3 main.py
```

5. 🐳 Build the container.

```bash
docker build -t morningbot .
```

6. 🐳 Run the container.

```bash
docker run -d --name morningbot morningbot
```