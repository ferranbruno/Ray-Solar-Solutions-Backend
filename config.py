import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///ray_solar.db'
    )

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    _raw_url = os.getenv('DATABASE_URL', '')
    # Render provides postgres:// but SQLAlchemy 2.x needs postgresql://
    _db_url = _raw_url.replace('postgres://', 'postgresql://', 1) if _raw_url else ''
    # Strip any existing sslmode param — we set it via connect_args
    if 'sslmode=' in _db_url:
        _db_url = _db_url.split('&sslmode=')[0].split('?sslmode=')[0]
    SQLALCHEMY_DATABASE_URI = _db_url or None
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 1,
        'max_overflow': 0,
        'pool_recycle': 180,
        'pool_pre_ping': True,
        'pool_timeout': 15,
        'connect_args': {
            'sslmode': 'disable',
            'connect_timeout': 10,
        },
    }

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
