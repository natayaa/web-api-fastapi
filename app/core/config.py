from pydantic import BaseModel, Field
from dotenv import load_dotenv


import os

# init load environment
load_dotenv()

class APPConfig(BaseModel):
    APP_HOST: str = Field(default_factory=lambda: os.getenv("APPLICATION_HOST", "localhost"))
    APP_PORT: int = Field(default_factory=lambda: os.getenv("APPLICATION_PORT", 80))
    APP_DEBUG: bool = Field(default_factory=lambda: os.getenv("APPLICATION_DEBUG", "false").lower() == "true")
    APP_SSLCERT: str = Field(default_factory=lambda: os.getenv("APPLICATION_SSLCERT_PATH"))
    APP_SSLPEM: str = Field(default_factory=lambda: os.getenv("APPLICATION_SSLPEM"))

    # CONFIG
    APP_APINAME: str = lambda: os.getenv("WEBAPI_NAME")
    APP_API_DEFAULT_PATH: str = Field(lambda: os.getenv("API_DEFAULT_PATH"))
    APP_API_DESC: str = "" # try to load from txt
    API_VERSION: str = lambda: os.getenv("API_VERSION")

   

class APIConfiguration(BaseModel):
    # API SECURITY CONFIGURATION
    API_ALGORITHM: str = Field(default_factory=lambda: os.getenv("API_SECURITY_ALGORITHM"))
    API_SECRET_KEY: str = Field(default_factory=lambda: os.getenv("API_SECRET_KEY"))
    API_REFRESH_SECRETKEY: str = Field(default_factory=lambda: os.getenv("API_REFRESH_SECRETKEY"))
    API_CSRF_SECRETKEY: str = Field(default_factory=lambda: os.getenv("API_CSRFKEY"))

    API_ACCESS_EXPIRES_MINUTES: int = os.getenv("API_ACCESS_EXPIRES_MINUTES", 15)
    API_REFRESH_EXPIRES_DAYS: int = os.getenv("API_REFRESH_EXPIRES_DAYS", 7)
    API_CSRF_EXPIRES_DAYS: int = os.getenv("API_CSRF_EXPIRES_DAYS")
    API_SESSION_ID_EXPIRES: int = os.getenv("API_SESSION_ID_EXPIRES", 1) # 1 day
    
    # HEADER SECURITY CONFIGURATION
    HEADERS_HTTP_ONLY: bool = Field(lambda: os.getenv("HEADERS_HTTP_ONLY", "false").lower() == "true")
    HEADERS_DEFAULT_PATH: str = Field(lambda: os.getenv("HEADERS_DEFAULT_PATH"))
    HEADERS_SAMESITE: str = Field(lambda: os.getenv("HEADERS_SAMESITE"))
    HEADERS_TOKEN_MAGAGE: int = Field(lambda: os.getenv("HEADERS_TOKEN_MAXAGE"))


class MongoDBConfiguration(BaseModel):
    SERVER_HOST: str = lambda: os.getenv("MONGO_SERVERHOST", "localhost")
    SERVER_PORT: int = lambda: os.getenv("MONGO_SERVERPORT", 27017)
    SERVER_USERNAME: str = lambda: os.getenv("MONGO_USERNAME")
    SERVER_PASSWORD: str = lambda: os.getenv("MONGO_PASSWORD")
    SERVER_DATABASE_NAME: str = lambda: os.getenv("MONGO_DATABASENAME")

    SERVER_STRING_CONFIG: str = f"mongodb://{SERVER_USERNAME}:{SERVER_PORT}@{SERVER_HOST}:{SERVER_PORT}/{SERVER_DATABASE_NAME}?authSource=admin"


class PostgresqlConfiguration(BaseModel):
    pass