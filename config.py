import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'xapp-xsd')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://dbuser:111222333@cluster0.4uumjvi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'xapp-xsd')
    DB_NAME = os.getenv('DB_NAME', 'flask_api')