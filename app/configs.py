from dotenv import load_dotenv
import os
import datetime

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    WTF_CSRF_ENABLED = False
    
    # JWT configurations
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_HEADER_NAME = os.getenv('JWT_HEADER_NAME', 'x-token')
    JWT_HEADER_TYPE = ''
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=2)