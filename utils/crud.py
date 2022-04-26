import os
import sqlalchemy
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.cursor import CursorResult
from utils.models import Filter, FilterCreate, FilterType, Transaction, TransactionCreate
from utils.cache import RedisCache
from utils.database import engine
import logging

cache: RedisCache = RedisCache(os.getenv("REDIS_HOST"),os.getenv("REDIS_PORT"))

async def get_transaction(db: AsyncSession, transaction_id: str):
    result = await db.execute(select(Transaction).filter(Transaction.txId == transaction_id).order_by(Transaction.created_dtz.desc()))
    return result.scalars().first()

async def insert_transaction(db: AsyncSession, transaction: TransactionCreate):
    db_transaction = Transaction(txId=transaction.txId,reward=transaction.reward,status=transaction.status,txType=transaction.txType)
    db.add(db_transaction)
    await db.commit()
    await db.refresh(db_transaction)
    return db_transaction

async def get_filter(db: AsyncSession, filter_name: str):
    result = await db.execute(select(Filter).filter(Filter.name == filter_name))
    return result.scalars().first()

async def get_filters(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Filter]:
    result = await db.execute(select(Filter).offset(skip).limit(limit))
    return result.scalars().all()

async def upsert_filter(db: AsyncSession, filter: FilterCreate):
    db_filter = Filter(name=filter.name,filterType=filter.filterType,repeats=filter.repeats,topics=filter.topics,messageTemplate=filter.messageTemplate,filterTree=filter.filterTree)
    await db.merge(db_filter)
    await db.commit()
    cache.setObject(f'filter_{filter.name}',db_filter)
    if filter.filterType == FilterType.BLOCK:
        block_filters: list[str] = cache.getObjectOrElse('block_filters',[])
        block_filters.append(filter.name)
        cache.setObject('block_filters',list(set(block_filters)))
    if filter.filterType == FilterType.UTXO:
        utxo_filters: list[str] = cache.getObjectOrElse('utxo_filters',[])
        utxo_filters.append(filter.name)
        cache.setObject('utxo_filters',list(set(utxo_filters)))
    if filter.filterType == FilterType.TX:
        tx_filters: list[str] = cache.getObjectOrElse('tx_filters',[])
        tx_filters.append(filter.name)
        cache.setObject('tx_filters',list(set(tx_filters)))
    return db_filter

async def delete_filter(db: AsyncSession, filter_name: str):
    query = sqlalchemy.delete(Filter).where(Filter.name == filter_name)
    result: CursorResult = await db.execute(query)
    await db.commit()
    if result.rowcount > 0:
        filter: Filter = cache.getObject(f'filter_{filter_name}')
        if filter.filterType == FilterType.BLOCK:
            block_filters: list[str] = cache.getObject('block_filters')
            block_filters.remove(filter.name)
            cache.setObject('block_filters',list(set(block_filters)))
        if filter.filterType == FilterType.UTXO:
            utxo_filters: list[str] = cache.getObject('utxo_filters')
            utxo_filters.remove(filter.name)
            cache.setObject('utxo_filters',list(set(utxo_filters)))
        if filter.filterType == FilterType.TX:
            tx_filters: list[str] = cache.getObject('tx_filters')
            tx_filters.remove(filter.name)
            cache.setObject('tx_filters',list(set(tx_filters)))
        cache.remove(f'filter_{filter_name}')
    return result.rowcount
