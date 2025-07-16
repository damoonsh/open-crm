from pydantic_settings import BaseSettings, SettingsConfigDict
import os, logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    PROJECT_NAME: str = "AuthService"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://db_user:${DB_PASSWORD}@localhost:5432/shared_db"
    )
    ALGORITHM: str = "RS256"  # Changed to RS256 for asymmetric keys
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    PRIVATE_KEY: str = ""
    PUBLIC_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    @property
    def private_key(self) -> str:
        return self.PRIVATE_KEY.replace("\\n", "\n")

    @property
    def public_key(self) -> str:
        return self.PUBLIC_KEY.replace("\\n", "\n")

settings = Settings()