import os
from dotenv import load_dotenv 
load_dotenv()

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    INTERP = os.environ.get('INTERP')
    ADMINS = ['info@runningdigitally.com']
    
    # Set Alpaca API key and secret
    api_key=os.getenv("ALPACA_API_KEY")

    # Create the Alpaca API object
    api_secret_key=os.getenv("ALPACA_SECRET_KEY")
    
    LANGUAGES = ['en', 'es']
    