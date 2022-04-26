from distutils.command.config import config
import os
from fastapi import APIRouter

config_router = APIRouter()

@config_router.get("/", name="config:get")
async def getConfig():
    return {
        'ERGO_EXPLORER': os.getenv('ERGO_EXPLORER'),
        'ERGO_NODE': os.getenv('ERGO_NODE'),
        'REDIS_HOST': os.getenv('REDIS_HOST'),
        'REDIS_PORT': os.getenv('REDIS_PORT'),
        'KAFKA_HOST': os.getenv('KAFKA_HOST'),
        'KAFKA_PORT': os.getenv('KAFKA_PORT'),
        'REWARD_ADDRESS': os.getenv('REWARD_ADDRESS')
    }