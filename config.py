import os

class Config:
    # Secret key for session management and other security-related needs
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # Database configuration, using environment variable or default local PostgreSQL database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://blog_user:yourpassword@localhost:5432/blog_db'
    
    # Disable modification tracking to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for JWT authentication
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_jwt_secret_key'
    
    # Cache configuration for Flask-Caching
    CACHE_TYPE = 'simple'  
    
    # Enable headers for rate limiting in Flask-Limiter
    RATELIMIT_HEADERS_ENABLED = True  

    # Regular expression for validating email addresses
    EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    # Minimum length for passwords
    PASSWORD_MIN_LENGTH = 8

class TestConfig(Config):
    # Enable testing mode
    TESTING = True
    
    # Use in-memory SQLite database for testing to avoid using actual database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable modification tracking to save resources during testing
    SQLALCHEMY_TRACK_MODIFICATIONS = False
