from typing import List
from pydantic import BaseSettings


class Settings(BaseSettings):
    _dbuser = "postgres"
    _dbpass = "postgres"
    _dbhost = "localhost"
    _dbport = "5432"
    _DATABASE_URL = f"postgresql://{_dbuser}:{_dbpass }@{_dbhost}:{_dbport}/idolbar"
    _host = "0.0.0.0"
    _port = 8001
    _isdebug = True
    _isreload = True
    SECRET_KEY: str = "idolbarAdmin2023!@#$#@!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 6000
    FILE_SESSION_TYPE = "memcached"
    FILE_SECRET_KEY = "idolbarAdmin2023!@#$"
    smspoh_host = "https://smspoh.com/api/"


class SMSPOH(BaseSettings):
    host = "https://smspoh.com/api"
    token = "1XPZ8f7pXFjW2Vey-_3yGIEcN5VPcj9nhot0JJX9DgtDTbBkF8EZhIvw1QctH8sM"

sms_api = SMSPOH()