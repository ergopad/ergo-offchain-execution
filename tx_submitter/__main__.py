import asyncio
import json
import logging
import os
import sys
import time
from fastapi import Depends
from kafka import KafkaConsumer
import requests
from filter_validator.FilterValidator import FilterValidator
from utils.cache import RedisCache
from utils import crud
from utils.database import engine
from utils.models import Transaction, TransactionCreate, TransactionStatus
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession


levelname = logging.DEBUG
logging.basicConfig(format='{asctime}:{name:>8s}:{levelname:<8s}::{message}', style='{', level=levelname)
logger = logging.getLogger('kafka')
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.WARN)

consumer = None
while consumer is None:
    try:
        consumer = KafkaConsumer('ergo.submit_tx',group_id='tx_submitters',bootstrap_servers=f"{os.getenv('KAFKA_HOST')}:{os.getenv('KAFKA_PORT')}",value_deserializer=lambda m: json.loads(m.decode('utf-8')))
    except:
        time.sleep(2)
res = requests.get(f'{os.getenv("ERGO_NODE")}/script/addressToTree/{os.getenv("REWARD_ADDRESS")}')
if res.ok:
    rewardErgoTree = res.json()["tree"]

logging.info(f"Reward ergo tree: {rewardErgoTree}")

async def main():

    for message in consumer:
        try:
            txReward = 0
            tx = message.value["tx"]
            txType = message.value["type"]
            for outp in tx["outputs"]:
                if outp["ergoTree"] == rewardErgoTree:
                    txReward += outp["value"]*10**-9
            res = requests.post(f'{os.getenv("ERGO_NODE")}/transactions',json=tx)
            if res.ok:
                db: AsyncSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)()
                db_tx = TransactionCreate(txId=tx["id"],reward=txReward,status=TransactionStatus.SUBMITTED,txType=txType)
                await crud.insert_transaction(db,db_tx)
                await db.close()
                logging.info(f"Submitted tx: {tx['id']}")
            else:
                logging.error(res.content)
        except Exception as e:
            logging.error(e)

if __name__ == "__main__":
    asyncio.run(main())
    