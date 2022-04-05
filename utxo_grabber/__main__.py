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

    producer = KafkaProducer(bootstrap_servers=f"{os.getenv('KAFKA_HOST')}:{os.getenv('KAFKA_PORT')}",value_serializer=lambda m: json.dumps(m).encode('utf-8'))

    cache: RedisCache = RedisCache(os.getenv("REDIS_HOST"),os.getenv("REDIS_PORT"))

    explorerHost: str = os.getenv("ERGO_EXPLORER")

    utxo_checkpoint: int = cache.getIntOrElse("utxo_grabber_checkpoint",0)

    block_checkpoint: int = cache.getIntOrElse("utxo_grabber_block_checkpoint",0)

    limit: int = 500

    while True:
        utxo_result: Response = requests.get(f"{explorerHost}/api/v1/boxes/byGlobalIndex/stream?minGix={utxo_checkpoint}&limit={limit}")

        if utxo_result.ok:
            boxesFound: int = 0
            for box in splitfile(BytesIO(utxo_result.content),format="json"):
                utxo = json.loads(box)
                if cache.getJsonOrElse(utxo["boxId"],None) is None:
                    cache.set(utxo["boxId"],box,3600)
                    producer.send('ergo.utxo',utxo)
                boxesFound += 1
            utxo_checkpoint += boxesFound
            cache.set("utxo_grabber_checkpoint",utxo_checkpoint)
            logging.info(f"Current UTXO checkpoint: {utxo_checkpoint}")

        block_result: Response = requests.get(f"{explorerHost}/api/v1/blocks?offset={block_checkpoint}&limit={limit}&sortDirection=asc")

        if block_result.ok:
            blocksFound: int = 0
            for block in block_result.json()["items"]:
                producer.send('ergo.blocks',block)
                blocksFound += 1
            block_checkpoint += blocksFound
            cache.set("utxo_grabber_block_checkpoint",block_checkpoint)
            logging.info(f"Current block checkpoint: {block_checkpoint}")
        # for box in result.:
        #     logging.info(box)
        # checkpoint += len(result)
        # logging.info(f"New checkpoint {checkpoint}")
        time.sleep(5)
