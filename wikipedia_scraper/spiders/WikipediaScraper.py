from gc import callbacks
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
import os
import urllib
import base64
from datetime import datetime

class WikipediaScraper(scrapy.Spider):
    name = "wikiscraper"
    allowed_domains = ["en.wikipedia.org","wiktionary.org","species.wikimedia.org"]
    start_urls = ["https://en.wikipedia.org/wiki/Wikipedia"]
    rules = (
        Rule(LinkExtractor(allow=r"wiki/"), callback='parse', follow=True)
    )

    def parse(self, response):        


        title = response.css('h1.firstHeading *::text').get()
        last_modified_date_raw = response.headers["last-modified"].decode('ascii')
        last_modified_date = datetime.fromtimestamp(datetime.strptime(last_modified_date_raw, "%a, %d %b %Y %H:%M:%S GMT").timestamp())

        yield {
            'Title' : title,
            'Url' : response.url,
            'Last Modified' : last_modified_date
        }

        self.write_to_disk(response)

        yield from response.follow_all(css='a', callback=self.parse)

    
    def write_to_disk(self,response):
        os.makedirs("./HTML_OUT", exist_ok=True)
        
        url_hash = hash(response.url)

        with open(f"./HTML_OUT/{url_hash}.html",'w+b') as file:
            file.write(response.body)

        
        
