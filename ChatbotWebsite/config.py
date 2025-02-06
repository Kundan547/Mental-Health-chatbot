import os
from dotenv import load_dotenv



# Load environment variables from a .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")
    
    # SQLAlchemy Database URI
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///site.db"  # Fallback to SQLite
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking for performance
    
    # Mail configuration
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI", "mysql+pymysql://root:password@localhost/dev_db"
    )


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI", "mysql+pymysql://root:password@localhost/prod_db"
    )
