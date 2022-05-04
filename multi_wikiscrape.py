import scrapy
import sys
import logging
from datetime import datetime
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

log = logging.getLogger(__name__)

#mongoDB connect DONE in settings/pipeline

class WikiSpider1(scrapy.Spider):
    def __init__(self, filename=None):
        if filename:
            with open(filename, 'r') as f:
                full = [url.strip() for url in f.readlines()]
                # split half of input file
                self.start_urls = full[:len(full)//2]
                print(self.start_urls)
        else:
            self.start_urls = ['https://en.wikipedia.org/wiki/Dog']
            
    name = "wiki"
    allowed_domains = ['wikipedia.org']
    # start_urls = ['https://en.wikipedia.org/wiki/Dog']
    #link extractor rule doesnt really work

    def parse(self, response):
        log.info('Parse function called on %s on spider %s', response.url,self.name)
        # page = response.url.split('/')[-1]
        # filename = 'wiki-%s.json' % page

        # Doesnt always return 
        # editDate = response.css('#footer-info-lastmod').re('\d+[A-Za-z\s]+\d+')
        # if editDate:
        #     editDate = response.css('#footer-info-lastmod').re('\d+[A-Za-z\s]+\d+')[0]
        
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

        #------------------------------------------------------------------------------------------
        #Get all href within content body (idk any more filenames that wiki has. Add any you find)
        #hrefText = response.css('#content a::attr(href)').re(r'^/wiki/.*(?<![.](?:gif|jpg|png|svg|tif|PNG|JPG|TIF|SVG|GIF))$')
        # stupid jpeg
        # hrefLinks = set([x for x in hrefText if not ('.jpeg' in x or '.JPEG' in x)])
        hrefLinks = set(response.css('#content a::attr(href)').re('^\/wiki\/(?!File:).*$'))
        #------------------------------------------------------------------------------------------
        yield from response.follow_all(hrefLinks, callback=self.parse)


# Testing out multiple spiders
class WikiSpider2(scrapy.Spider):
    # for CLI seed.txt
    def __init__(self, filename=None):
        if filename:
            with open(filename, 'r') as f:
                full = [url.strip() for url in f.readlines()]
                # split half of input file
                self.start_urls = full[len(full)//2:]
                print(self.start_urls)
        else:
            self.start_urls = ['https://en.wikipedia.org/wiki/Cat']

    name = "wiki2"
    allowed_domains = ['wikipedia.org']

    def parse(self, response):
        log.info('Parse function called on %s on spider %s', response.url,self.name)
        # page = response.url.split('/')[-1]
        # filename = 'wiki-%s.json' % page

        # Doesnt always return 
        # editDate = response.css('#footer-info-lastmod').re('\d+[A-Za-z\s]+\d+')
        # if editDate:
        #     editDate = response.css('#footer-info-lastmod').re('\d+[A-Za-z\s]+\d+')[0]

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
            'img': response.css('.infobox img::attr(src),.infobox-full-data img::attr(src), .thumbinner img::attr(src)').get()
        }

        #------------------------------------------------------------------------------------------
        #Get all href within content body (idk any more filenames that wiki has. Add any you find)
        # hrefText = response.css('#content a::attr(href)').re(r'^/wiki/.*(?<![.](?:gif|jpg|png|svg|tif|PNG|JPG|TIF|SVG|GIF))$')
        # stupid jpeg
        #hrefLinks = set([x for x in hrefText if not ('.jpeg' in x or '.JPEG' in x or '.tiff')])
        hrefLinks = set(response.css('#content a::attr(href)').re('^\/wiki\/(?!File:).*$'))
        #------------------------------------------------------------------------------------------
        yield from response.follow_all(hrefLinks, callback=self.parse)


def main(filename=None, cset=None):
    configure_logging()
    settings = get_project_settings()
    if cset:
        for k,v in cset.items():
            settings[k] = v
    
    runner = CrawlerRunner(settings)
    runner.crawl(WikiSpider2,filename)
    runner.crawl(WikiSpider1,filename)
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()

if __name__ == '__main__':
    if(len(sys.argv)>1):
        if '=' in sys.argv[1]:
            main(None, dict(arg.split('=') for arg in sys.argv[1:]))
        else:
            main(sys.argv[1], dict(arg.split('=') for arg in sys.argv[2:]))
    else:
        main()