import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv

from mongo import Mongo

load_dotenv()
MONGO_HOST = os.getenv('MONGO_HOST', 'mongo')
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'sampleDB')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION', 'sample_collection')
MONGO_USERNAME = os.getenv('MONGO_USERNAME', 'user')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', 'password')

dt_from = datetime.fromisoformat('2022-09-01T00:00:00')
dt_upto = datetime.fromisoformat('2022-12-31T23:59:00')
group_type = 'month'


async def main():
    print('\nfind:')
    query = {'dt': {'$gt': dt_from, '$lt': dt_upto}}
    result = await mongo.find(query, limit=5)
    async for line in result:
        print(line)

    print('\naggregate:')
    pipeline = [
        {'$match': {'dt': {'$gte': dt_from, '$lte': dt_upto}}},
        {
            '$group': {
                '_id': {'$dateTrunc': {'date': '$dt', 'unit': group_type}},
                'total': {'$sum': '$value'},
            }
        },
        {'$sort': {'_id': 1}},
    ]
    result = await mongo.aggregate(pipeline)
    async for line in result:
        print(line)


if __name__ == '__main__':
    mongo = Mongo(
        MONGO_HOST,
        MONGO_PORT,
        MONGO_DATABASE,
        MONGO_COLLECTION,
        MONGO_USERNAME,
        MONGO_PASSWORD,
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
