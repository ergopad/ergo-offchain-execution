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

    tx_checkpoint: int = cache.getIntOrElse("utxo_grabber_tx_checkpoint",0)

    block_checkpoint: int = cache.getIntOrElse("utxo_grabber_block_checkpoint",0)

    if tx_checkpoint == 0 or block_checkpoint == 0:
        networkState_response: Response = requests.get(f"{ergoNode}/info")
        if networkState_response.ok:
            block_checkpoint = networkState_response.json()["fullHeight"]
            block_transactions_response = requests.get(f"{ergoNode}/blocks/{networkState_response.json()['bestFullHeaderId']}/transactions")
            if block_transactions_response.ok:
                tx_info_response = requests.get(f"{ergoNode}/blockchain/transaction/byId/{block_transactions_response.json()['transactions'][0]['id']}")
                if tx_info_response.ok:
                    tx_checkpoint = tx_info_response.json()["globalIndex"]

    limit: int = 500

    while True:
        try:
            sleeptime = 5
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

            findingMoreTransactions = True
            while findingMoreTransactions:
                tx_result: Response = requests.get(f"{ergoNode}/blockchain/transaction/byIndex/{tx_checkpoint}")

                if tx_result.ok:
                    tx = tx_result.json()
                    producer.send('ergo.tx',tx)
                    for utxo in tx["outputs"]:
                        producer.send('ergo.utxo',utxo)
                    tx_checkpoint += 1
                    cache.set("utxo_grabber_tx_checkpoint",tx_checkpoint)
                    logging.info(f"Current TX checkpoint: {tx_checkpoint}")
                else:
                    findingMoreTransactions = False

            block_result: Response = requests.get(f"{ergoNode}/blocks/chainSlice?fromHeight={block_checkpoint}&toHeight={block_checkpoint+limit}&sortDirection=asc")

            if block_result.ok:
                blocksFound: int = 0
                for block in block_result.json():
                    if block["height"] > block_checkpoint:
                        producer.send('ergo.blocks',block)
                        blocksFound += 1
                block_checkpoint += blocksFound
                if blocksFound == limit:
                    sleeptime = 0.1
                cache.set("utxo_grabber_block_checkpoint",block_checkpoint)
                logging.info(f"Current block checkpoint: {block_checkpoint}")
        except Exception as e:
            logging.error(e)
        time.sleep(sleeptime)
