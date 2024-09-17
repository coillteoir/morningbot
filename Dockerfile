from python:3.11-slim

workdir /workspace/morningbot

copy requirements.txt requirements.txt
run pip install -r requirements.txt

copy bot bot
copy leaderboard leaderboard

cmd ["python3", "."]
