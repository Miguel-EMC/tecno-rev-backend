import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings"""

    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", ""

    # Application
    APP_NAME: str = "Tecno Rev API"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"


settings = Settings()
