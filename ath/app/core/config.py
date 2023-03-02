import secrets
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings

from app.enums.visualization import RenderingFormat


class Settings(BaseSettings):
    DEBUG: bool = False

    PROJECT_NAME: str = "ath"
    API_V1_STR: str = "/api/v1"
    API_APP: str = "app.main:app"
    PORT: int = 9000

    API_CLIENT_KEY: str
    API_CLIENT_SECRET: str

    TUSD_HOST: str
    TUSD_PORT: str
    TUSD_ENDPOINT: str
    TUSD_UPLOAD_CHUNK: int

    S3_HOST: str
    S3_PORT: str
    S3_REGION: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_CSVS_BUCKET_NAME: str
    S3_PLOTS_BUCKET_NAME: str

    S3_HOST_EXT: str
    S3_PORT_EXT: str

    VISUALIZATION_RENDERING_FORMAT: Optional[RenderingFormat] = RenderingFormat.PNG

    SECRET_KEY: str = secrets.token_urlsafe(32)

    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    DATABASE_URL: str
    TEST_DATABASE_URL: Optional[str] = None

    class Config:
        case_sensitive: bool = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
