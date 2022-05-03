# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
from scrapy.utils.project import get_project_settings
import logging
from scrapy.exceptions import DropItem

log = logging.getLogger(__name__)
settings = get_project_settings()

class MongoDBPipeline(object):

    def __init__(self, mongo_server, mongo_port):
        self.mongo_server = mongo_server
        self.mongo_port = mongo_port
        self.url_seen = set()

    @classmethod
    def from_crawler(cls, crawler):
        ## pull in information from settings.py
        return cls(
            mongo_server = crawler.settings.get('MONGODB_SERVER'),
            mongo_port = crawler.settings.get('MONGODB_PORT')
        )

    def open_spider(self, spider):
        ## initializing spider
        ## opening db connection
        self.client = pymongo.MongoClient(
            settings.get('MONGODB_SERVER'),
            settings.get('MONGODB_PORT')
        )
        self.db = self.client[settings.get('MONGODB_DB')]
        self.collection = self.db[settings.get('MONGODB_COLLECTION')]
        #create index on url to keep unique
        self.collection.create_index([("url", pymongo.ASCENDING)],unique = True)   

    def close_spider(self, spider):
        ## clean up when spider is closed
        self.client.close()

    def process_item(self, item, spider):
        try:
            self.collection.insert_one(item)
        except:
            raise DropItem("Duplicate item title found: %s" % item)

        # if item['url'] in self.url_seen:
        #     raise DropItem("Duplicate item title found: %s" % item)
        # else:
        #     self.url_seen.add(item['url'])
        #     self.collection.update_one(item,upsert=True)
        #     return item

class WikipediaScraperPipeline:
    def process_item(self, item, spider):
        return item
