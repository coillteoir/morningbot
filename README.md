# MorningBot

MorningBot is a Discord Bot which allows admins to reward users for wishing eachother good morning. Since every server is unique morningbot allows admins to configure the bot and run it themselves. There is a base configuraion which serves as an example and is used in the main instance of morningbot. 

## Planned features
- Leaderboard functionality
- Leaderboard winner gets a custom role
- Multi-channel config for more expressive bots.

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

5. 🐳 Build the image.

```bash
docker build -t morningbot .
```

6. 🐳 Run the container.

```bash
docker run -d --name morningbot morningbot
```


### Current supported Languages
"good morning" - English
"maidin mhaith" - Irish
"buenos días" - Spanish
"bonjour" - French
"guten morgen" - German
"buongiorno" - Italian
"bom dia" - Portuguese
"доброе утро" - Russian
"早上好" - Chinese
"おはようございます" - Japanese
"좋은 아침입니다" - Korean
"صباح الخير" - Arabic
"सुप्रभात" - Hindi
"habari za asubuhi" - Swahili
"καλημέρα" - Greek
"günaydın" - Turkish
"god morgon" - Swedish
"dzień dobry" - Polish
"בוקר טוב" - Hebrew
"สวัสดีตอนเช้า" - Thai
"hyvää huomenta" - Finnish
"god morgen" - Norwegian
"buna dimineata" - Romanian
"bore da" - Hausa
"beyanî baş" - Kurdish
"bonum mane" - Latin
"dobro jutro" - Croatian
"dobré ráno" - Czech
"dobrý deň" - Slovak
"labas rytas" - Lithuanian
"labrīt" - Latvian
"magandang umaga" - Fillipino
"ata mārie" - Maori
"chào buổi sáng" - Vietnamese
"өглөөний мэнд" - Mongolian