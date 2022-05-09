from gc import callbacks
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
import os
import urllib
import base64
from datetime import datetime


class WikipediaScraper(scrapy.spiders.CrawlSpider):
    name = "wikiscraper"
    allowed_domains = ["en.wikipedia.org","www.wiktionary.org", "species.wikimedia.org"]
    start_urls = ["https://en.wikipedia.org/wiki/Statue_of_Liberty"]

    # A link extractor that will extract all links from the page
    general_link_extractor = LinkExtractor()

    # A link extractor that will extract only links to wikipedia article pages
    wikipedia_link_extractor = LinkExtractor(allow=(r"wikipedia\.org\/wiki\/[^:]*$", ))

    # Configure the spider to only crawl article pages
    rules = (
        Rule(wikipedia_link_extractor, callback="parse", follow=True),
    )

    def parse(self, response):
        # Scrape the title from the first heading
        title = response.css('h1.firstHeading *::text').get()

        # Parse the modification date using the HTTP last-modified header
        last_modified_date_raw = response.headers["last-modified"].decode('ascii')
        last_modified_date = datetime.strptime(last_modified_date_raw, "%a, %d %b %Y %H:%M:%S GMT")

        # Gets the object's coordinates from the wikipedia page if it has any
        coordinates = None
        if (response.css('span.geo-dms').get() is not None):
            latitude = response.css('span.latitude::text').get()
            longitude = response.css('span.longitude::text').get()
            coordinates = (latitude, longitude)

        # Gets the subheaders from the wikipedia page
        subheaders = response.css('span.mw-headline::text').getall()
        
        # Gets the categories that the article is a member of
        categories = response.xpath('//div[@class="mw-normal-catlinks"]/ul/li/a/text()').getall()
        print(f"FOUND CATEGORIES {categories}")

        # Gets the links that the article has (including fragments)
        links_and_fragments = self.general_link_extractor.extract_links(response)
        
        # Filter for only links without fragments (to avoid links to the same page)
        links = [link.url for link in links_and_fragments if link.fragment == ""]

        # Gets the number of sources that the article has
        num_of_references = len(response.css("ol.references li").getall())

        # Returns the article's metadata
        yield {
            'Title': title,
            'Url': response.url,
            'Last Modified': last_modified_date,
            'Coordinates': coordinates,
            'Number of References': num_of_references,
            'Subheaders': subheaders,
            'Categories': categories,
            'Links': links
        }

        # Write the wikipedia html file to disk
        self.write_to_disk(response)

    def write_to_disk(self, response):
        # Make the html output folder if it doesn't exist
        os.makedirs("./HTML_OUT", exist_ok=True)

        # Turn the url into a hash to avoid filename edge cases
        url_hash = hash(response.url)

        # Write the html file to disk
        with open(f"./HTML_OUT/{url_hash}.html", 'w+b') as file:
            file.write(response.body)
