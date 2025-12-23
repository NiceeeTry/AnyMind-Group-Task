import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class Settings:
    """Application settings loaded from environment variables"""
    
    # Database (using psycopg async driver)
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/pos_db"
    
    app_name: str = "POS E-commerce Platform"

    host: str = "0.0.0.0"
    port: int = 8000
    
    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables"""
        return cls(
            database_url=os.getenv(
                "DATABASE_URL",
                "postgresql+psycopg://postgres:postgres@localhost:5432/pos_db"
            ),
            app_name=os.getenv("APP_NAME", "POS E-commerce Platform"),
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
        )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings.from_env()

