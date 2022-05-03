import scrapy
import logging
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

log = logging.getLogger(__name__)

#mongoDB connect DONE in settings/pipeline

class WikiSpider1(scrapy.Spider):
    custom_settings = {}
    def __init__(self, filename=None):
        if filename:
            with open(filename, 'r') as f:
                self.start_urls = [url.strip() for url in f.readlines()]
        
    name = "wiki"
    allowed_domains = ['wikipedia.org']
    print(custom_settings)
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
            'italicText': ' '.join(response.css('#content p i::text').re('.{2,}')).lower()
        }

        #------------------------------------------------------------------------------------------
        #Get all href within content body
        hrefText = response.css('#content a::attr(href)').re(r'^/wiki/.*(?<![.](?:jpg|png|svg))$')
        # joins href with domain 
        nextPages = set([response.urljoin(link) for link in hrefText])
        #------------------------------------------------------------------------------------------
        yield from response.follow_all(nextPages, callback=self.parse)

# class WikiSpider2(scrapy.Spider):
#     name = "wiki2"
#     allowed_domains = ['wikipedia.org']

#     def parse(self, response):
#         log.info('Parse function called on %s', response.url)
#         page = response.url.split('/')[-1]
#         filename = 'wiki-%s.json' % page

#         editDate = response.css('#footer-info-lastmod').re('\d+[A-Za-z\s]+\d+')
#         if editDate:
#             editDate = response.css('#footer-info-lastmod').re('\d+[A-Za-z\s]+\d+')[0]

#         yield {
#             'url': response.url,
#             'title': response.css('title::text').get(),
#             'editDate': editDate,
#             'TOC': response.css('.toc .toctext::text').getall(),
#             'mainText': ' '.join(response.css('#content p::text, #content a::text').re('[A-Za-z0-9\-]+')).lower(),
#             'boldText': ' '.join(response.css('#content p b::text').re('.{2,}')).lower(),
#             'italicText': ' '.join(response.css('#content p i::text').re('.{2,}')).lower()
#         }

#         # try:
#         #     # with open("pages/"+filename,"w") as f:
#         #     #     json.dump(scraped,f)
#         #     collection.insert_one(scraped)
#         # except:
#         #     log.debug("Error creating file")
        
        
#         # Testing stuff some explainations on regex chosen
#         #---------------------------------------------------------------------------------------------
#         # mainText = response.css('p::text').getall()
#         #get all bold text 2+ characters because wiki does a,b,c,d list
#         # boldText = response.css('b::text').re('\w{2,}')

#         # title of wiki page
#         # titleArticle = response.css('#firstHeading::text').get()
#         #title of website
#         # titlePage = response.css('title::text').get()
#         # tocText = response.css('.toc .toctext::text').getall()

#         # regex for only /wiki/ links
#         # not too worried about duplicates because will be putting in set later
#         #---------------------------------------------------------------------------------------------

#         #---------------------------------------------------------------------------------------------
#         # This yields write to one file with command "scrapy crawl wiki -O wiki.json" 
#         #            -O: append to file 
#         #            -O: create new file
#         #            instead of yield we can just insert into mongo

#         #prob need to do some error checking if null
#         # try:
#             # yield{
#             #     'id': hashlib.sha256(str(response.url).encode('utf-8')).hexdigest()
#             #     'url': response.url,
#             #     'title': response.css('#firstHeading::text').get(),
#             #     'mainText': ' '.join(response.css('p::text').re('[^\n].*')),
#             #     'boldText': response.css('b::text').re('.{2,}'),
#             #     'TOC': response.css('.toc .toctext::text').getall(),
#             #     'editDate': response.css('#footer-info-lastmod').re('\d+[A-Za-z\s]+\d+')[0]
#             # }
#         # except:
#         #     log.debug("Yikes")
#         #---------------------------------------------------------------------------------------------

#         #Get all href within content body
#         hrefText = response.css('#content a::attr(href)').re('/wiki/.*')
#         # joins href with domain 
#         nextPages = set([response.urljoin(link) for link in hrefText])
#         yield response.follow_all(nextPages, callback=self.parse)


if __name__ == '__main__':
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(WikiSpider1)
    #process.crawl(WikiSpider2)
    process.start() 