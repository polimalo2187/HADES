# core/database.py

from pymongo import MongoClient
from core.config import Config
from core.logger import get_logger

logger = get_logger(__name__)


class MongoDB:
    _client = None
    _db = None

    @classmethod
    def connect(cls):
        if cls._client is None:
            try:
                cls._client = MongoClient(Config.MONGO_URI)
                cls._db = cls._client[Config.MONGO_DB_NAME]
                logger.info("Conectado a MongoDB correctamente")
            except Exception as e:
                logger.error(f"Error conectando a MongoDB: {e}")
                raise e

        return cls._db

    @classmethod
    def get_db(cls):
        if cls._db is None:
            return cls.connect()
        return cls._db
