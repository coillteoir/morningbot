FROM python:3.11-slim

FROM gorialis/discord.py

RUN mkdir -p /usr/src/MorningBot

WORKDIR /usr/src/MorningBot

COPY . .

CMD ["python3", "."]
