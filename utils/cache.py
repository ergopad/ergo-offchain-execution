import sys
from redis import Redis
import json
import logging

class RedisCache:
    def __init__(self, redisHost: str, redisPort: str, defaultTimeout: int = -1) -> None:
        self.redisHost = redisHost
        self.redisPort = redisPort
        self.defaultTimeout = defaultTimeout
        self.client = Redis(self.redisHost,self.redisPort)

    def getInt(self, key: str) -> int:
        return int(self.client.get(key))

    def getIntOrElse(self, key: str, default: int) -> int:
        try:
            return self.getInt(key)
        except Exception as e:
            logging.error(e)
            return default

    def getJson(self, key: str):
        return json.loads(self.client.get(key))

    def getJsonOrElse(self, key: str, default):
        try:
            return self.getJson(key)
        except:
            return default

    def getStr(self, key: str) -> str:
        return str(self.client.get(key))

    def getStrOrElse(self, key: str, default: str):
        try:
            return self.getStr(key)
        except:
            return default

    def set(self, key: str, value, timeout: int = None):
        if timeout is None:
            timeout = self.defaultTimeout
        if timeout == -1:
            self.client.set(key,value)
        else:
            self.client.setex(key,timeout,value)

    @property
    def redisHost(self) -> str:
        return self._redisHost
    
    @redisHost.setter
    def redisHost(self, value: str):
        self._redisHost = value

    @property
    def redisPort(self) -> str:
        return self._redisPort
    
    @redisPort.setter
    def redisPort(self, value: str):
        self._redisPort = value

    @property
    def defaultTimeout(self) -> int:
        return self._defaultTimeout
    
    @defaultTimeout.setter
    def defaultTimeout(self, value: int):
        self._defaultTimeout = value

    @property
    def client(self) -> Redis:
        return self._client

    @client.setter
    def client(self, value: Redis):
        self._client = value