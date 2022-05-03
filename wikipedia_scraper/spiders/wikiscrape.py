import scrapy
import logging
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import re

log = logging.getLogger(__name__)

#mongoDB connect DONE in settings/pipeline

class WikiSpider1(scrapy.Spider):
    def __init__(self, filename=None):
        if filename:
            with open(filename, 'r') as f:
                self.start_urls = [url.strip() for url in f.readlines()]
        else:
            self.start_urls = ['https://en.wikipedia.org/wiki/Dog']
        
    name = "wiki"
    allowed_domains = ['wikipedia.org']
    # start_urls = ['https://en.wikipedia.org/wiki/Dog']
    #link extractor rule doesnt really work

    def parse(self, response):
        log.info('Parse function called on %s', response.url)
        page = response.url.split('/')[-1]
        filename = 'wiki-%s.json' % page

        # Doesnt always return 
        # editDate = response.css('#footer-info-lastmod').re('\d+[A-Za-z\s]+\d+')
        # if editDate:
        #     editDate = response.css('#footer-info-lastmod').re('\d+[A-Za-z\s]+\d+')[0]
        
        last_modified_date_raw = None
        if response.headers.has_key('last-modified'):
            last_modified_date_raw = response.headers["last-modified"].decode('ascii')
            last_modified_date  = datetime.fromtimestamp(
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

        #------------------------------------------------------------------------------------------
        #Get all href within content body (idk any more filenames that wiki has. Add any you find)
        hrefText = response.css('#content a::attr(href)').re(r'^/wiki/.*(?<![.](?:gif|jpg|png|svg|tif|tif|PNG))$')
        # stupid jpeg
        hrefLinks = set([x for x in hrefText if not '.jpeg' in x])
        #------------------------------------------------------------------------------------------
        yield from response.follow_all(hrefLinks, callback=self.parse)


# Testing out multiple spiders
class WikiSpider2(scrapy.Spider):
    # for CLI seed.txt
    def __init__(self, filename=None):
        if filename:
            with open(filename, 'r') as f:
                self.start_urls = [url.strip() for url in f.readlines()]
        else:
            self.start_urls = ['https://en.wikipedia.org/wiki/Cat']

    name = "wiki2"
    allowed_domains = ['wikipedia.org']
    # start_urls = ['https://en.wikipedia.org/wiki/Dog']
    # link extractor rule doesnt really work

    def parse(self, response):
        log.info('Parse function called on %s', response.url)
        # page = response.url.split('/')[-1]
        # filename = 'wiki-%s.json' % page

        # Doesnt always return 
        # editDate = response.css('#footer-info-lastmod').re('\d+[A-Za-z\s]+\d+')
        # if editDate:
        #     editDate = response.css('#footer-info-lastmod').re('\d+[A-Za-z\s]+\d+')[0]

        last_modified_date_raw = None
        if response.headers.has_key('last-modified'):
            last_modified_date_raw = response.headers["last-modified"].decode('ascii')
            last_modified_date  = datetime.fromtimestamp(
                datetime.strptime(last_modified_date_raw, "%a, %d %b %Y %H:%M:%S GMT").timestamp())

        yield {
            'url': response.url,
            'title': response.css('title::text').get(),
            'lastMod': last_modified_date,
            'TOC': response.css('.toc .toctext::text').getall(),
            'mainText': ' '.join(response.css('#content p::text, #content a::text').re('[A-Za-z0-9\-]+')).lower(),
            'boldText': ' '.join(response.css('#content p b::text').re('.{2,}')).lower(),
            'italicText': ' '.join(response.css('#content p i::text').re('.{2,}')).lower(),
            'img': response.css('.infobox img::attr(src),.infobox-full-data img::attr(src), .thumbinner img::attr(src)').get()
        }

        #------------------------------------------------------------------------------------------
        #Get all href within content body (idk any more filenames that wiki has. Add any you find)
        hrefText = response.css('#content a::attr(href)').re(r'^/wiki/.*(?<![.](?:gif|jpg|png|svg|tif|PNG))$')
        # stupid jpeg
        hrefLinks = set([x for x in hrefText if not '.jpeg' in x])
        #------------------------------------------------------------------------------------------
        yield from response.follow_all(hrefLinks, callback=self.parse)


if __name__ == '__main__':
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(WikiSpider1)
    process.crawl(WikiSpider2)
    process.start() 