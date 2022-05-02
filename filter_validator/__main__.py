import asyncio
import json
import logging
import os
import sys
import time
from fastapi import Depends
from kafka import KafkaConsumer
from filter_validator.FilterValidator import FilterValidator
from utils.cache import RedisCache
from utils import crud
from utils.database import engine
from utils.models import Filter, FilterType
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession


levelname = logging.DEBUG
logging.basicConfig(format='{asctime}:{name:>8s}:{levelname:<8s}::{message}', style='{', level=levelname)
logger = logging.getLogger('kafka')
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.WARN)

cache: RedisCache = RedisCache(os.getenv("REDIS_HOST"),os.getenv("REDIS_PORT"))
consumer = None
while consumer is None:
    try:
        consumer = KafkaConsumer('ergo.utxo','ergo.blocks','ergo.tx',group_id='filter-validators',bootstrap_servers=f"{os.getenv('KAFKA_HOST')}:{os.getenv('KAFKA_PORT')}",value_deserializer=lambda m: json.loads(m.decode('utf-8')))
    except:
        time.sleep(2)

async def refreshFilterCache():
    db: AsyncSession = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )()
    filters = await crud.get_filters(db,0,1000000)
    await db.close()
    block_filters = []
    utxo_filters = []
    tx_filters = []
    for filter in filters:
        filterValidator = filter
        cache.setObject(f'filter_{filter.name}',filterValidator)
        if filter.filterType == FilterType.BLOCK:
            block_filters.append(filter.name)     
        if filter.filterType == FilterType.UTXO:
            utxo_filters.append(filter.name)
        if filter.filterType == FilterType.TX:
            tx_filters.append(filter.name)
    cache.setObject('utxo_filters',utxo_filters)
    cache.setObject('block_filters',block_filters)
    cache.setObject('tx_filters',tx_filters)

async def main():
    await refreshFilterCache()

    for message in consumer:
        try:
            if message.topic == 'ergo.utxo':
                filters: list[str] = cache.getObject('utxo_filters')          
            if message.topic == 'ergo.blocks':
                filters: list[str] = cache.getObject('block_filters')
            if message.topic == 'ergo.tx':
                filters: list[str] = cache.getObject('tx_filters')
            for filter in filters:
                filterValidator: FilterValidator = FilterValidator(cache.getObject(f'filter_{filter}'))
                filterValidator.process(message.value)
        except Exception as e:
            logging.error(e)

if __name__ == "__main__":
    asyncio.run(main())
    