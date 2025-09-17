from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


class Settings(BaseSettings):
    TOKEN : str
    pg_host : str
    pg_port : int
    pg_database : str
    pg_username : str
    pg_password : str

    @property
    def DB_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.pg_username}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_database}"
    
    @property
    def DB_URL_psycopg(self):
        return f"postgresql+psycopg://{self.pg_username}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_database}"

    @property
    def sessionM(self):
        return sessionmaker(
            f"postgresql+asyncpg://{self.pg_username}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_database}", class_=AsyncSession, expire_on_commit=False
        )

    model_config = SettingsConfigDict(env_file=".env")
    
    

settings = Settings()