from motor.motor_asyncio import AsyncIOMotorClient


class Mongo:
    def __init__(self, host, port, database, collection, username, password):
        self.client = AsyncIOMotorClient(
            host=host, port=port, username=username, password=password
        )
        self.db = self.client.get_database(database)
        self.collection = self.db.get_collection(collection)

    async def find(self, query, limit=0):
        return self.collection.find(query).limit(limit)

    async def aggregate(self, pipeline):
        return self.collection.aggregate(pipeline)
