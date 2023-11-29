FROM python:3.11-slim

WORKDIR /usr/src/MorningBot
COPY . .
RUN pip install -r requirements.txt

CMD ["python3", "."]
