import asyncio
import json
import sys
import time
from typing import List
import os
import logging
import requests
from requests.models import Response
from splitstream import splitfile
from io import BytesIO
from utils.cache import RedisCache
from kafka import KafkaProducer, KafkaConsumer

if __name__ == "__main__":
    levelname = logging.DEBUG
    logging.basicConfig(format='{asctime}:{name:>8s}:{levelname:<8s}::{message}', style='{', level=levelname)
    logger = logging.getLogger('kafka')
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.WARN)

    producer = None
    while producer is None:
        try:
            producer = KafkaProducer(bootstrap_servers=f"{os.getenv('KAFKA_HOST')}:{os.getenv('KAFKA_PORT')}",value_serializer=lambda m: json.dumps(m).encode('utf-8'))
        except:
            time.sleep(2)

    cache: RedisCache = RedisCache(os.getenv("REDIS_HOST"),os.getenv("REDIS_PORT"))

    explorerHost: str = os.getenv("ERGO_EXPLORER")
    ergoNode: str = os.getenv("ERGO_NODE")

    tx_checkpoint: int = cache.getIntOrElse("utxo_grabber_tx_checkpoint",2980000)

    block_checkpoint: int = cache.getIntOrElse("utxo_grabber_block_checkpoint",726000)

    limit: int = 500

    while True:
        try:
            mempoolOffset = 0
            mempoolLimit = 100
            mempoolScanDone = False
            mempoolTransactions = []
            while not mempoolScanDone:
                mempool_result: Response = requests.get(f"{ergoNode}/transactions/unconfirmed?offset={mempoolOffset}&limit={mempoolLimit}")
                if mempool_result.ok:
                    mempoolTransactions = mempoolTransactions + list(mempool_result.json())
                if len(mempool_result.json()) < mempoolLimit:
                    mempoolScanDone = True
                mempoolOffset += mempoolLimit
                    
            for mempoolTx in mempoolTransactions:
                if cache.getJsonOrElse(mempoolTx["id"],None) is None:
                    cache.set(mempoolTx["id"],1,3600)
                    producer.send('ergo.tx',mempoolTx)
                    for mempoolUtxo in mempoolTx["outputs"]:
                        producer.send('ergo.utxo',mempoolUtxo)
                
            tx_result: Response = requests.get(f"{explorerHost}/api/v1/transactions/byGlobalIndex/stream?minGix={tx_checkpoint}&limit={limit}")

            if tx_result.ok:
                txFound: int = 0
                for rawTx in splitfile(BytesIO(tx_result.content),format="json"):
                    tx = json.loads(rawTx)
                    producer.send('ergo.tx',tx)
                    txFound += 1
                    for utxo in tx["outputs"]:
                        producer.send('ergo.utxo',utxo)
                tx_checkpoint += txFound
                cache.set("utxo_grabber_tx_checkpoint",tx_checkpoint)
                logging.info(f"Current TX checkpoint: {tx_checkpoint}")

            block_result: Response = requests.get(f"{explorerHost}/api/v1/blocks?offset={block_checkpoint}&limit={limit}&sortDirection=asc")

            if block_result.ok:
                blocksFound: int = 0
                for block in block_result.json()["items"]:
                    producer.send('ergo.blocks',block)
                    blocksFound += 1
                block_checkpoint += blocksFound
                cache.set("utxo_grabber_block_checkpoint",block_checkpoint)
                logging.info(f"Current block checkpoint: {block_checkpoint}")
        except Exception as e:
            logging.error(e)
        time.sleep(5)
