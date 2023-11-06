import asyncio
import os
from datetime import datetime

from dateutil.relativedelta import relativedelta  # type: ignore
from dotenv import load_dotenv

from mongo import Mongo

load_dotenv()
MONGO_HOST = os.getenv('MONGO_HOST', 'mongo')
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'sampleDB')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION', 'sample_collection')
MONGO_USERNAME = os.getenv('MONGO_USERNAME', 'user')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', 'password')

dt_from = datetime.fromisoformat('2022-10-01T00:00:00')
dt_upto = datetime.fromisoformat('2022-11-30T23:59:00')
group_type = 'day'


def get_next_dt(dt: datetime, period: str) -> datetime:
    if period == 'hour':
        return dt + relativedelta(hours=1)
    elif period == 'day':
        return dt + relativedelta(days=1)
    elif period == 'month':
        return dt + relativedelta(months=1)
    return dt_upto


async def get_dataset():
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
    dataset, labels = [], []
    next_dt = dt_from
    async for line in await mongo.aggregate(pipeline):
        while line['_id'] > next_dt < dt_upto:
            dataset.append(0)
            labels.append(next_dt.isoformat())
            next_dt = get_next_dt(next_dt, group_type)
        dataset.append(line['total'])
        labels.append(line['_id'].isoformat())
        next_dt = get_next_dt(next_dt, group_type)

    result = {'dataset': dataset, 'labels': labels}
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
    loop.run_until_complete(get_dataset())
    print(dt_from, get_next_dt(dt_upto, 'hour'))
