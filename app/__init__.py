from flask import Flask
from flask_cors import CORS
from app.extensions import mongo
import os
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Configuration from environment variables
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/webhooks')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Enable CORS for all routes
    CORS(app)
    
    # Initialize extensions
    mongo.init_app(app)
    
    # Register blueprints
    from app.webhook.routes import webhook
    app.register_blueprint(webhook)
    
    return app