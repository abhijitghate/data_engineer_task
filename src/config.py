import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://scope_admin:supersecretpassword@localhost:5432/scope_ratings"
    )

settings = Settings()