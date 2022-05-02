import scrapy
# from urllib.parse import urlparse
# from urllib.parse import urljoin
import logging
import json

log = logging.getLogger(__name__)

class WikiSpider(scrapy.Spider):
    name = "wiki"
    start_urls = [
        'https://en.wikipedia.org/wiki/Dmitry_Lebed'
    ]

    def parse(self, response):
        page = response.url.split('/')[-1]
        filename = 'wiki-%s.json' % page

        scraped = {
                'url': response.url,
                'title': response.css('#firstHeading::text').get(),
                'mainText': ' '.join(response.css('p::text').re('[^\n].*')),
                'boldText': response.css('b::text').re('.{2,}'),
                'TOC': response.css('.toc .toctext::text').getall(),
                'editDate': response.css('#footer-info-lastmod').re('\d+[A-Za-z\s]+\d+')[0]
                }
        try:
            with open("pages/"+filename,"w") as f:
                json.dump(scraped,f)
        except:
            log.debug("Error creating file")
        
        # Testing stuff some explainations on regex chosen
        #---------------------------------------------------------------------------------------------
        # mainText = response.css('p::text').getall()
        #get all bold text 2+ characters because wiki does a,b,c,d list
        # boldText = response.css('b::text').re('\w{2,}')

        # title of wiki page
        # titleArticle = response.css('#firstHeading::text').get()
        #title of website
        # titlePage = response.css('title::text').get()
        # tocText = response.css('.toc .toctext::text').getall()

        # regex for only /wiki/ links
        # not too worried about duplicates because will be putting in set later
        #---------------------------------------------------------------------------------------------

        #---------------------------------------------------------------------------------------------
        # This yields write to one file with command "scrapy crawl wiki -O wiki.json" 
        #            -O: append to file 
        #            -O: create new file
        #            instead of yield we can just insert into mongo

        #prob need to do some error checking if null
        # try:
            # yield{
            #     'url': response.url,
            #     'title': response.css('#firstHeading::text').get(),
            #     'mainText': ' '.join(response.css('p::text').re('[^\n].*')),
            #     'boldText': response.css('b::text').re('.{2,}'),
            #     'TOC': response.css('.toc .toctext::text').getall(),
            #     'editDate': response.css('#footer-info-lastmod').re('\d+[A-Za-z\s]+\d+')[0]
            # }
        # except:
        #     log.debug("Yikes")
        #---------------------------------------------------------------------------------------------

        hrefText = response.css('a::attr(href)').re('/wiki/.*')
        # joins href with domain 
        nextPages = set([response.urljoin(link) for link in hrefText])
        # TODO: follow next link 

   

