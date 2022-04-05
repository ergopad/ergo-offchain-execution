import os
from ergo_offchain_api.models.filter import Filter
from utils.cache import RedisCache
from fastapi import APIRouter

cache = RedisCache(os.getenv("REDIS_HOST"),os.getenv("REDIS_PORT"))

filter_router = APIRouter()

@filter_router.post("/filter/", name="filter:new")
async def newFilter(req: Filter):
    return {'validation': 'success'}