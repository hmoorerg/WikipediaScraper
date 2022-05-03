import scrapy
import logging
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

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

        editDate = response.css('#footer-info-lastmod').re('\d+[A-Za-z\s]+\d+')
        if editDate:
            editDate = response.css('#footer-info-lastmod').re('\d+[A-Za-z\s]+\d+')[0]

        yield {
            'url': response.url,
            'title': response.css('title::text').get(),
            'editDate': editDate,
            'TOC': response.css('.toc .toctext::text').getall(),
            'mainText': ' '.join(response.css('#content p::text, #content a::text').re('[A-Za-z0-9\-]+')).lower(),
            'boldText': ' '.join(response.css('#content p b::text').re('.{2,}')).lower(),
            'italicText': ' '.join(response.css('#content p i::text').re('.{2,}')).lower(),
            'img': response.css('.infobox img::attr(src), .infobox-full-data img::attr(src), .thumbinner img::attr(src)').get()
        }

        #------------------------------------------------------------------------------------------
        #Get all href within content body (idk any more filenames that wiki has. Add any you find)
        hrefText = response.css('#content a::attr(href)').re(r'^/wiki/.*(?<![.](?:gif|jpeg|jpg|png|svg|tif))$')
        # joins href with domain 
        nextPages = set([response.urljoin(link) for link in hrefText])
        #------------------------------------------------------------------------------------------
        yield from response.follow_all(nextPages, callback=self.parse)


# Testing out multiple spiders
class WikiSpider2(scrapy.Spider):
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

        editDate = response.css('#footer-info-lastmod').re('\d+[A-Za-z\s]+\d+')
        if editDate:
            editDate = response.css('#footer-info-lastmod').re('\d+[A-Za-z\s]+\d+')[0]

        yield {
            'url': response.url,
            'title': response.css('title::text').get(),
            'editDate': editDate,
            'TOC': response.css('.toc .toctext::text').getall(),
            'mainText': ' '.join(response.css('#content p::text, #content a::text').re('[A-Za-z0-9\-]+')).lower(),
            'boldText': ' '.join(response.css('#content p b::text').re('.{2,}')).lower(),
            'italicText': ' '.join(response.css('#content p i::text').re('.{2,}')).lower(),
            'img': response.css('.infobox img::attr(src),.infobox-full-data img::attr(src), .thumbinner img::attr(src)').get()
        }

        #------------------------------------------------------------------------------------------
        #Get all href within content body (idk any more filenames that wiki has. Add any you find)
        hrefText = response.css('#content a::attr(href)').re(r'^/wiki/.*(?<![.](?:gif|jpeg|jpg|png|svg|tif))$')
        # joins href with domain 
        nextPages = set([response.urljoin(link) for link in hrefText])
        #------------------------------------------------------------------------------------------
        yield from response.follow_all(nextPages, callback=self.parse)


if __name__ == '__main__':
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(WikiSpider1)
    process.crawl(WikiSpider2)
    process.start() 