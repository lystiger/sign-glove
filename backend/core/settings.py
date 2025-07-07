#For MongoDB offline

from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    DB_NAME: str = "sign_language_glove"

    class Config:
        env_file = ".env"  # optionally load from .env file

settings = Settings()
