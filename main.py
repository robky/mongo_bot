import asyncio
import json
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from dateutil.relativedelta import relativedelta  # type: ignore

from config import app_settings, logger
from mongo import Mongo

CORRECT_INTERVAL = ('hour', 'day', 'month')

mongo = Mongo(
    app_settings.mongo_host,
    app_settings.mongo_port,
    app_settings.mongo_database,
    app_settings.mongo_collection,
    app_settings.mongo_username,
    app_settings.mongo_password.get_secret_value(),
)

bot = Bot(token=app_settings.bot_token.get_secret_value())
dp = Dispatcher()


def get_next_dt(dt: datetime, period: str) -> datetime:
    match period:
        case 'hour':
            return dt + relativedelta(hours=1)
        case 'day':
            return dt + relativedelta(days=1)
        case _:
            return dt + relativedelta(months=1)


async def main():
    await dp.start_polling(bot)


@dp.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(
        'Агрегации статистических данных о зарплатах '
        'сотрудников. Введите запрос.'
    )


@dp.message(F.text)
async def get_request(message: Message):
    logger.info(f'Получен запрос: {message.text}')
    try:
        data = json.loads(message.text)
        dt_from = datetime.fromisoformat(data['dt_from'])
        dt_upto = datetime.fromisoformat(data['dt_upto'])
        group_type = data['group_type']
        if group_type not in CORRECT_INTERVAL:
            raise
    except Exception as err:
        logger.error(f'Ошибка запроса: {message.text} -> {err}')
        await message.answer('Неподдерживаемый запрос')
        return
    try:
        answer = await get_dataset(dt_from, dt_upto, group_type)
        await message.answer(answer)
    except Exception as err:
        logger.error(f'Ошибка получения данных -> {err}')
        await message.answer('При формировании ответа произошла ошибка.')


async def get_dataset(
    dt_from: datetime, dt_upto: datetime, group_type: str
) -> str:
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
    while next_dt <= dt_upto:
        dataset.append(0)
        labels.append(next_dt.isoformat())
        next_dt = get_next_dt(next_dt, group_type)
    return json.dumps({'dataset': dataset, 'labels': labels})


if __name__ == '__main__':
    logger.info('Старт бота')
    asyncio.run(main())
