# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import pymongo
import json

class MongoDBPipeline(object):
    def __init__(self, mongo_server, mongo_port, mongo_db, mongo_collection):
        self.mongo_server = mongo_server
        self.mongo_port = mongo_port
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection

    @classmethod
    def from_crawler(cls, crawler):
        ## pull in information from settings.py
        return cls(
            mongo_server = crawler.settings.get('MONGODB_SERVER'),
            mongo_port = crawler.settings.get('MONGODB_PORT'),
            mongo_db = crawler.settings.get('MONGODB_DB', 'WikiScrape'),
            mongo_collection = crawler.settings.get('MONGODB_COLLECTION', 'Pages')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(
            self.mongo_server,
            self.mongo_port,
            connectTimeoutMS=3000,
            serverSelectionTimeoutMS=3000
        )
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.mongo_collection]
        #create index on url to keep unique
        self.collection.create_index([("url", pymongo.ASCENDING)],unique = True)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        try:
            self.collection.update_one({'url': item['url']}, {"$set": item }, upsert=True)
        except:
            raise DropItem("Error adding item to DB with url: %s" % item['url'])

class StoreLocalPipeline:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            output_dir = crawler.settings.get('output_dir')
        )

    def process_item(self, item, spider):
        page = item['url'].split('/')[-1]
        filename = '%s/wiki-%s.json' % (self.output_dir,page)
        with open(filename, 'w') as f:
            json.dump(item,f,default=str)
        return item

class WikipediaScraperPipeline:
    def process_item(self, item, spider):
        return item
