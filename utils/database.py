from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from config import Config
import logging
import certifi
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        try:
            # Add tlsCAFile=certifi.where() to fix SSL issues
            self.client = MongoClient(
                os.getenv("MONGO_URI"),
                tlsCAFile=certifi.where(),
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                serverSelectionTimeoutMS=30000
            )
            # Verify the connection
            self.client.admin.command('ping')
            self.db = self.client[os.getenv("DB_NAME", "knowledge_base")]
            logger.info("Successfully connected to MongoDB")
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {e}")
            self.client = None
            self.db = None
        except ConfigurationError as e:
            logger.error(f"MongoDB configuration error: {e}")
            self.client = None
            self.db = None
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            self.client = None
            self.db = None
    
    def get_db(self):
        if self.db is None:
            self.connect()
        return self.db
    
    def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Singleton instance
mongo = MongoDB()