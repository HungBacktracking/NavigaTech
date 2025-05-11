from motor.motor_asyncio import AsyncIOMotorClient

class MongoDB:
    def __init__(self, mongo_url: str, db_name: str):
        self.mongo_url = mongo_url
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[db_name]

