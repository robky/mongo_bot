import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv

from mongo import Mongo

load_dotenv()
MONGO_HOST = os.getenv('MONGO_HOST', 'mongo')
MONGO_PORT = os.getenv('MONGO_PORT', 27017)
MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'sampleDB')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION', 'sample_collection')
MONGO_USERNAME = os.getenv('MONGO_USERNAME', 'user')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', 'password')


async def main():
    query = {
        'dt': {
            '$gt': datetime.fromisoformat(
                '2022-01-01T03:20:00.000Z'.replace('Z', '')
            ),
            '$lt': datetime.fromisoformat(
                '2022-01-01T03:30:00.000Z'.replace('Z', '')
            ),
        }
    }
    result = await mongo.find(query)
    print(result)


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
