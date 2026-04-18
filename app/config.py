import logging

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    ADMIN_EMAIL: str = "admin@pcb.com"
    ADMIN_PASSWORD: str = "admin123"

    class Config:
        env_file = ".env"
        extra = "ignore"

    def debug_print(self):
        logger.info(f"✅ Settings loaded:")
        logger.info(f"   DATABASE_URL: {self.DATABASE_URL[:50]}...")
        logger.info(f"   ADMIN_EMAIL: {self.ADMIN_EMAIL}")


settings = Settings()
