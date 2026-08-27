import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration settings."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'cinescope-fallback-secret-key-9999')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///cinescope.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # TMDB Settings
    TMDB_API_KEY = os.getenv('TMDB_API_KEY', '').strip()
    # Use api.tmdb.org instead of api.themoviedb.org to bypass ISP blocks in certain regions
    TMDB_BASE_URL = 'https://api.tmdb.org/3'
    TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p'
    
    # Session / Cache
    API_CACHE_EXPIRY_HOURS = 24

    # Firebase Client SDK Config
    FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY', '')
    FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN', '')
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', '')
    FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET', '')
    FIREBASE_MESSAGING_SENDER_ID = os.getenv('FIREBASE_MESSAGING_SENDER_ID', '')
    FIREBASE_APP_ID = os.getenv('FIREBASE_APP_ID', '')
