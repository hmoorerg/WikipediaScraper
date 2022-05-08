FROM python:3.10-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["scrapy","crawl","wikiscraper"]