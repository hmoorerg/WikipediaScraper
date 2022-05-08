import pymongo
from itemadapter import ItemAdapter

class MongoPipeline:
    collection_name = 'scrapy_items'

    def __init__(self, mongo_uri, mongo_db, collection_name, username, password):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.username = username
        self.password = password
        self.collection_name = collection_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI', 'mongodb://localhost:27017'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'Wikipedia'),
            collection_name=crawler.settings.get('MONGO_COLLECTION', 'Articles'),
            username=crawler.settings.get('MONGO_USERNAME'),
            password=crawler.settings.get('MONGO_PASSWORD')
        )

    def open_spider(self, spider):

        # Select client based on whether we're using a username and password
        if self.username is None or self.password is None:
            self.client = pymongo.MongoClient(self.mongo_uri)
        else:
            self.client = pymongo.MongoClient(self.mongo_uri, username=self.username, password=self.password)
        
        self.db = self.client[self.mongo_db]

        self.db[self.collection_name].create_index([('Url', pymongo.ASCENDING)], unique=True)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        data = ItemAdapter(item).asdict()

        self.db[self.collection_name].update_one({'Url': data['Url']}, {'$set': data}, upsert=True)
        return item