from pydantic import BaseModel, Field
from typing import Literal, Optional
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()


class APPConfig(BaseModel):
    APP_ENVIRONMENT: Literal['dev', 'staging', 'prod'] = Field(default_factory=lambda: os.getenv("APPLICATION_ENVIRONMENT", "dev"))
    APP_HOST: str = Field(default_factory=lambda: os.getenv("APPLICATION_HOST", "localhost"))
    APP_PORT: int = Field(default_factory=lambda: int(os.getenv("APPLICATION_PORT", 8000)))
    APP_DEBUG: bool = Field(default_factory=lambda: os.getenv("APPLICATION_DEBUG", "false").lower() == "true")
    APP_SSLCERT: Optional[str] = Field(default_factory=lambda: os.getenv("APPLICATION_SSLCERT_PATH"))
    APP_SSLPEM: Optional[str] = Field(default_factory=lambda: os.getenv("APPLICATION_SSLPEM"))

    # Metadata
    APP_APINAME: Optional[str] = Field(default_factory=lambda: os.getenv("WEBAPI_NAME", "FastAPI Application"))
    APP_API_DEFAULT_PATH: Optional[str] = Field(default_factory=lambda: os.getenv("API_DEFAULT_PATH", "/api"))
    
    # Load API description from file if exists
    APP_API_DESC: str = Field(default_factory=lambda: open("description.txt").read() if os.path.exists("description.txt") else "")
    API_VERSION: Optional[str] = Field(default_factory=lambda: os.getenv("API_VERSION", "1.0.0"))
    API_DOCS_ENABLE: bool = Field(default_factory=lambda: os.getenv("API_DOCS_ENABLE", "true").lower() == "true")

    # Monitoring
    API_PROMETHEUS: bool = Field(default_factory=lambda: os.getenv("API_PROMETHEUS", "false").lower() == "true")


class APIConfiguration(BaseModel):
    API_ALGORITHM: str = Field(default_factory=lambda: os.getenv("API_SECURITY_ALGORITHM", "HS256"))
    API_SECRET_KEY: str = Field(default_factory=lambda: os.getenv("API_SECRET_KEY"))
    API_REFRESH_SECRETKEY: str = Field(default_factory=lambda: os.getenv("API_REFRESH_SECRETKEY"))
    API_CSRF_SECRETKEY: str = Field(default_factory=lambda: os.getenv("API_CSRFKEY"))

    API_ACCESS_EXPIRES_MINUTES: int = Field(default_factory=lambda: int(os.getenv("API_ACCESS_EXPIRES_MINUTES", 15)))
    API_REFRESH_EXPIRES_DAYS: int = Field(default_factory=lambda: int(os.getenv("API_REFRESH_EXPIRES_DAYS", 7)))
    API_CSRF_EXPIRES_DAYS: int = Field(default_factory=lambda: int(os.getenv("API_CSRF_EXPIRES_DAYS", 2)))
    API_SESSION_ID_EXPIRES: int = Field(default_factory=lambda: int(os.getenv("API_SESSION_ID_EXPIRES", 1)))  # 1 day

    # Header settings
    HEADERS_HTTP_ONLY: bool = Field(default_factory=lambda: os.getenv("HEADERS_HTTP_ONLY", "true").lower() == "true")
    HEADERS_DEFAULT_PATH: str = Field(default_factory=lambda: os.getenv("HEADERS_DEFAULT_PATH", "/"))
    HEADERS_SAMESITE: str = Field(default_factory=lambda: os.getenv("HEADERS_SAMESITE", "Lax"))
    HEADERS_TOKEN_MAGAGE: int = Field(default_factory=lambda: int(os.getenv("HEADERS_TOKEN_MAXAGE", 86400)))  # 1 day


class MongoDBConfiguration(BaseModel):
    SERVER_HOST: str = Field(default_factory=lambda: os.getenv("MONGO_SERVERHOST", "localhost"))
    SERVER_PORT: int = Field(default_factory=lambda: int(os.getenv("MONGO_SERVERPORT", 27017)))
    SERVER_USERNAME: Optional[str] = Field(default_factory=lambda: os.getenv("MONGO_USERNAME"))
    SERVER_PASSWORD: Optional[str] = Field(default_factory=lambda: os.getenv("MONGO_PASSWORD"))
    SERVER_DATABASE_NAME: str = Field(default_factory=lambda: os.getenv("MONGO_DATABASENAME", "test"))

    @property
    def SERVER_STRING_CONFIG(self) -> str:
        if self.SERVER_USERNAME and self.SERVER_PASSWORD:
            return f"mongodb://{self.SERVER_USERNAME}:{self.SERVER_PASSWORD}@{self.SERVER_HOST}:{self.SERVER_PORT}/{self.SERVER_DATABASE_NAME}?authSource=admin"
        return f"mongodb://{self.SERVER_HOST}:{self.SERVER_PORT}/{self.SERVER_DATABASE_NAME}"


class PostgresqlConfiguration(BaseModel):
    # Prefer full connection URL if set
    DATABASE_URL: str = Field(
        default_factory=lambda: os.getenv("POSTGRES_DATABASE_URL") or
        f"postgresql://{os.getenv('POSTGRES_USER', 'user')}:{os.getenv('POSTGRES_PASSWORD', 'pass')}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'database')}"
    )

    # Connection settings
    DATABASE_POOL_SIZE: int = Field(default_factory=lambda: int(os.getenv("POSTGRES_POOL_SIZE", 10)))
    DATABASE_MAX_OVERFLOW: int = Field(default_factory=lambda: int(os.getenv("POSTGRES_MAX_OVERFLOW", 20)))
    DATABASE_TIMEOUT: int = Field(default_factory=lambda: int(os.getenv("POSTGRES_TIMEOUT", 30)))  # seconds
    DATABASE_ECHO: bool = Field(default_factory=lambda: os.getenv("POSTGRES_ECHO", "false").lower() == "true")
    DATABASE_SSLMODE: str = Field(default_factory=lambda: os.getenv("POSTGRES_SSLMODE", "prefer"))

    # Optional debugging or development switches
    USE_ASYNC_DRIVER: bool = Field(default_factory=lambda: os.getenv("POSTGRES_USE_ASYNC", "false").lower() == "true")

    def sqlalchemy_url(self) -> str:
        if self.USE_ASYNC_DRIVER:
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        return self.DATABASE_URL