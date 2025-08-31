from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from routes.user_routes import init_user_routes
from routes.project_routes import init_project_routes
from routes.rag_routes import init_rag_routes
from utils.database import mongo
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Register routes
    init_user_routes(app)
    init_project_routes(app)
    init_rag_routes(app)
    
    # Verify MongoDB connection 
    @app.before_request
    def verify_db_connection():
        if not hasattr(app, 'db_checked'):
            db = mongo.get_db()
            if db is None:
                logger.error("Failed to connect to MongoDB - check your connection settings")
            else:
                logger.info("MongoDB connection verified")
            app.db_checked = True
    
    # Close MongoDB connection - teardown
    # @app.teardown_appcontext
    # def teardown_db(exception):
    #     mongo.close()
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Check MongoDB connection before starting
    if mongo.get_db() is None:
        logger.error("Application starting without database connection!")
    else:
        logger.info("Database connection established")
    
    app.run(debug=True)