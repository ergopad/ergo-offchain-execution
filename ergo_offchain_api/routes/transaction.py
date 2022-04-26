from http.client import HTTPException
import logging
import os
from utils.models import Transaction, TransactionCreate
from utils.cache import RedisCache
from utils.database import get_session
from utils import crud
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


transaction_router = APIRouter()

@transaction_router.post("/", name="transaction:new", response_model=Transaction)
async def newTransaction(req: TransactionCreate, db: AsyncSession = Depends(get_session)):
    return await crud.insert_transaction(db,req)

@transaction_router.get("/get/{txId}", name="transaction:getById", response_model=Transaction)
async def getTransaction(txId: str, db: AsyncSession = Depends(get_session)):
    db_transaction = await crud.get_transaction(db,txId)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction