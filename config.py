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
    # Ensure sslmode=require is present for Render PostgreSQL
    if _db_url and 'sslmode=' not in _db_url:
        separator = '&' if '?' in _db_url else '?'
        _db_url += f'{separator}sslmode=require'
    SQLALCHEMY_DATABASE_URI = _db_url or None
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 2,
        'max_overflow': 2,
        'pool_recycle': 120,
        'pool_pre_ping': True,
        'pool_timeout': 10,
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
