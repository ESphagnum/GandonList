from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import Any


class Settings(BaseSettings):
    TOKEN: str
    
    guild_id: int
    admin_role_id: int
    developer_role_id: int

    pg_host: str
    pg_port: int
    pg_database: str
    pg_username: str
    pg_password: str
    pg_echo: bool

    @property
    def DB_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.pg_username}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_database}"

    @property
    def DB_URL_psycopg(self):
        return f"postgresql+psycopg://{self.pg_username}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_database}"

    @property
    def DB_ECHO(self):
        return self.pg_echo

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
