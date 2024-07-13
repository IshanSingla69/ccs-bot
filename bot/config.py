import pymongo
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    mongo_client = None

    @classmethod
    def initialize_mongo_client(cls, url):
        if cls.mongo_client is None:
            cls.mongo_client = pymongo.MongoClient(url)


Config.initialize_mongo_client(os.getenv("MONGO_URL"))
