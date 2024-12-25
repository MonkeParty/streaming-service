from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path.cwd()/'.env-example', env_file_encoding='utf-8')

    minio_root_user: str
    minio_root_password: str
    minio_endpoint_url: str
    minio_bucket: str
    minio_port: int
    minio_console_port: int

settings = Settings()