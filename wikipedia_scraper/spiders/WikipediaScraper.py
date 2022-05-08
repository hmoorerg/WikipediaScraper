from gc import callbacks
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
import os
import urllib
import base64
from datetime import datetime
from scrapy.http import Request


class Article(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    last_modified_date = scrapy.Field()
    coordinates = scrapy.Field()
    categories = scrapy.Field()
    subheaders = scrapy.Field()
    popularity = scrapy.Field()



class WikipediaScraper(scrapy.spiders.CrawlSpider):
    name = "wikiscraper"
    allowed_domains = ["en.wikipedia.org", "wikidata.org"]
    start_urls = ["https://en.wikipedia.org/wiki/Statue_of_Liberty"]
    rules = (
        Rule(LinkExtractor(allow=(r"wikidata.org\/wiki\/", )), follow=False),

        Rule(LinkExtractor(allow=(r"wikipedia\.org\/wiki\/[^:]*$", )), callback="parse"),
    )

    def parse(self, response):
        title = response.css('h1.firstHeading *::text').get()
        last_modified_date_raw = response.headers["last-modified"].decode('ascii')
        last_modified_date = datetime.strptime(last_modified_date_raw, "%a, %d %b %Y %H:%M:%S GMT")

        coordinates = None
        if (response.css('span.geo-dms').get() is not None):
            latitude = response.css('span.latitude::text').get()
            longitude = response.css('span.longitude::text').get()
            coordinates = (latitude, longitude)

        subheaders = response.css('span.mw-headline::text').getall()
        
        # Combine the data we have so far for this page
        item = Article()
        item['title'] = title
        item['last_modified_date'] = last_modified_date
        item['coordinates'] = coordinates
        item['subheaders'] = subheaders
        item['url'] = response.url

        # Gets the url to the articles's information page    
        wikimedia_path = response.css('#t-wikibase a::attr(href)').get()
        page_info_path = response.css('#t-info a::attr(href)').get()
        
        # Writes the html file to disk
        self.write_to_disk(response)
        
        # Continues parsing by visiting the page information and wikidata pages
        return response.follow(wikimedia_path, callback=self.parse_wikidata, cb_kwargs = dict(item=item))

    def parse_page_information(self, response, item):

        self.logger.info("Visited %s", response.url)
        print()
        print()
        print("parsing page information")
        print()
        print()
        item["Popularity"] = "Test Value"
        
        # Get the link to the wikimedia page
        
        # yield response.follow(wikimedia_path, callback=self.parse_wikimedia, cb_kwargs = dict(item=item), dont_filter=True)
        return item

    def parse_wikidata(self, response, item):
        print()
        print()
        print("parsing page information")
        print()
        print()

        self.logger.info("Visited %s", response.url)
        
        # Get the type of item that the wikidata page is about
        item.categories = response.css('#mw-data-entity-type::text').getall()
        return item


    def write_to_disk(self, response):
        os.makedirs("./HTML_OUT", exist_ok=True)

        url_hash = hash(response.url)

        with open(f"./HTML_OUT/{url_hash}.html", 'w+b') as file:
            file.write(response.body)
