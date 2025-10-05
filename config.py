import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = False
    TESTING = False

class SandboxConfig(Config):
    """Sandbox configuration"""
    PESAPAL_BASE_URL = "https://cybqa.pesapal.com/pesapalv3"
    CONSUMER_KEY = os.getenv('PESAPAL_SANDBOX_CONSUMER_KEY')
    CONSUMER_SECRET = os.getenv('PESAPAL_SANDBOX_CONSUMER_SECRET')
    CALLBACK_URL = os.getenv('PESAPAL_SANDBOX_CALLBACK_URL', 'http://localhost:5000/payment/callback')

class ProductionConfig(Config):
    """Production configuration"""
    PESAPAL_BASE_URL = "https://pay.pesapal.com/v3"
    CONSUMER_KEY = os.getenv('PESAPAL_PRODUCTION_CONSUMER_KEY')
    CONSUMER_SECRET = os.getenv('PESAPAL_PRODUCTION_CONSUMER_SECRET')
    CALLBACK_URL = os.getenv('PESAPAL_PRODUCTION_CALLBACK_URL')

config = {
    'sandbox': SandboxConfig,
    'production': ProductionConfig,
    'default': SandboxConfig
}