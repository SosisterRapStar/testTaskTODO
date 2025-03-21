from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict, BaseSettings
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class BSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",  # здесь можно менять окружение на тестовое
    )


class DBSettings(BSettings):
    db_user: str = Field(default="user", alias="DB_USER")
    db_password: str = Field(default="1234", alias="DB_PASSWORD")
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: str = Field(default="5432", alias="DB_PORT")
    db_name: str = Field(default="postgres", alias="DB_NAME")

    @property
    def db_string_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


class SecuritySettings(BSettings):
    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_algo: str = Field(alias="JWT_ALGO")
    access_token_expire_minutes: int = Field(
        default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_minutes: int = Field(
        default=120, alias="REFRESH_TOKEN_EXPIRE_MINUTES"
    )


class Settings(BaseModel):
    db: DBSettings = DBSettings()
    security: SecuritySettings = SecuritySettings()


settings = Settings()


# Подключение логера
logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)
# midnight параметр отвечает за обновление соответсвенно в полночь
# handler = TimedRotatingFileHandler(
#     "/app/logs/app.log", when="midnight", interval=1, backupCount=7
# )
# handler.suffix = "%Y-%m-%d"
# formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
# handler.setFormatter(formatter)
# logger.addHandler(handler)

# # отключение INFO и DEBUG логов sqlalchemy
# logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
