import os
import scrapy
import logging
import argparse
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

log = logging.getLogger(__name__)

class WikiSpider(scrapy.Spider):
    def __init__(self, filename=None):
        if filename:
            with open(filename, 'r') as f:
                self.start_urls = [url.strip() for url in f.readlines()]
        else:
            self.start_urls = ['https://en.wikipedia.org/wiki/Dog']        
            
    name = "wiki"
    allowed_domains = ['wikipedia.org']

    def parse(self, response):
        log.info('Parse function called on %s on spider %s', response.url,self.name)

        last_modified_date = None
        if response.headers.has_key('last-modified'):
            last_modified_date_raw = response.headers["last-modified"].decode('ascii')
            last_modified_date = datetime.fromtimestamp(
                datetime.strptime(last_modified_date_raw, "%a, %d %b %Y %H:%M:%S GMT").timestamp())

        yield {
            'url': response.url,
            'title': response.css('title::text').get(),
            'lastMod': last_modified_date,
            'TOC': response.css('.toc .toctext::text').getall(),
            'mainText': ' '.join(response.css('#content p::text, #content a::text').re('[A-Za-z0-9\-]+')).lower(),
            'boldText': ' '.join(response.css('#content p b::text').re('.{2,}')).lower(),
            'italicText': ' '.join(response.css('#content p i::text').re('.{2,}')).lower(),
            'img': response.css('.infobox img::attr(src), .infobox-full-data img::attr(src), .thumbinner img::attr(src)').get()
        }

        hrefLinks = set(response.css('#content a::attr(href)').re('^\/wiki\/(?!File:).*$'))
        yield from response.follow_all(hrefLinks, callback=self.parse)

def main():
    parser = argparse.ArgumentParser(description="Crawler options. To configure mongoDB connection, please edit project settings.py")
    parser.add_argument('-i', '--infile', metavar='', type=argparse.FileType('r'), help="Input seed file of urls")
    parser.add_argument('-p', '--num_page', metavar='', type=int, help="Page limit on crawl (default = inf)")
    parser.add_argument('-d', '--depth', metavar='', type=int, help="Depth limit on crawl (default = inf)")
    parser.add_argument('-o', '--output', metavar='', type=str, 
            help="Output directory to store scraped pages. Creates directory if doesn't exist")
    parser.add_argument('-m', '--mongo', action='store_true', help="Option to enable mongo pipeline. Configure settings in settings.py")
    parser.add_argument('-s', '--silent', action='store_true', help="Option to supress log to INFO")
    args = parser.parse_args()

    settings = get_project_settings()
    if args.output:
        os.makedirs(f"{args.output}", exist_ok=True)
        settings['FEED_EXPORT_BATCH_ITEM_COUNT'] = 1
        settings['FEEDS'] = {
           f"{args.output}/%(batch_id)d-page%(batch_time)s.json" : {
               'format' : 'json',
               'encoding': 'utf8',
               'item_export_kwargs': {
                    'export_empty_fields': True,
                }
           }
        }
        #settings['ITEM_PIPELINES']['wikipedia_scraper.pipelines.StoreLocalPipeline'] = 200
        settings['output_dir'] = args.output
    if args.depth:
        settings['DEPTH_LIMIT'] = args.depth
    if args.num_page:
        settings['CLOSESPIDER_PAGECOUNT'] = args.num_page
    if args.silent:
        settings['LOG_LEVEL'] = "INFO"
    if args.mongo:
        settings['ITEM_PIPELINES']['wikipedia_scraper.pipelines.MongoDBPipeline'] = 100

    process = CrawlerProcess(settings)
    process.crawl(WikiSpider,args.infile)
    process.start()

if __name__ == "__main__":
    main()


