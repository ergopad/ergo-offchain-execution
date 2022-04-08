from http.client import HTTPException
import logging
import os
from utils.models import Filter, FilterCreate, validateFilterNode, FilterValidationException
from utils.cache import RedisCache
from utils.database import get_session
from utils import crud
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

cache = RedisCache(os.getenv("REDIS_HOST"),os.getenv("REDIS_PORT"))

filter_router = APIRouter()

@filter_router.post("/", name="filter:new", response_model=Filter)
async def newFilter(req: FilterCreate, db: AsyncSession = Depends(get_session)):
    try:
        validateFilterNode(req.filterType,req.filterTree)
    except FilterValidationException as fve:
        return {
            'validation': 'error',
            'message': fve.message,
            'FilterNode': fve.node
        }

    return await crud.upsert_filter(db,req)

@filter_router.get("/get/{name}", name="filter:getById", response_model=Filter)
async def getFilter(name: str, db: AsyncSession = Depends(get_session)):
    db_filter = await crud.get_filter(db,name)
    if db_filter is None:
        raise HTTPException(status_code=404, detail="Filter not found")
    return db_filter

@filter_router.get("/list", name="filter:getFiltersList", response_model=list[Filter])
async def getFilters(skip: int, limit: str, db: AsyncSession = Depends(get_session)):
    db_filters = await crud.get_filters(db,skip,limit)
    if db_filters is None:
        raise HTTPException(status_code=404, detail="No filters found")
    return db_filters

@filter_router.get("/delete/{name}", name="filter:deleteById")
async def deleteFilter(name: str, db: AsyncSession = Depends(get_session)):
    deleted = await crud.delete_filter(db,name)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Filter not found")
    return