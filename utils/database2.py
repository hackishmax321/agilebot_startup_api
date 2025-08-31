from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

mongo = PyMongo()

def get_db():
    """Get the MongoDB database instance"""
    try:
        return mongo.db
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        return None

def get_knowledge_base_collection():
    """
    Get the knowledge base collection from MongoDB.
    This collection stores metadata about documents added to the RAG system.
    """
    try:
        db = get_db()
        if db is None:
            logger.error("Cannot access knowledge base - no database connection")
            return None
        
        # Create collection if it doesn't exist
        collection_name = "knowledge_base"
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
            logger.info(f"Created new collection: {collection_name}")
        
        return db[collection_name]
    except Exception as e:
        logger.error(f"Error accessing knowledge base collection: {e}")
        return None

def init_db(app):
    """Initialize MongoDB connection"""
    try:
        mongo.init_app(app)
        # Verify connection by trying to access a collection
        get_db()
        logger.info("MongoDB initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing MongoDB: {e}")