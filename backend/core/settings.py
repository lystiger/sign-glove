"""
Settings for MongoDB connection and environment configuration in the sign glove system.

- Settings: Loads MongoDB URI and database name, optionally from a .env file.
"""
#For MongoDB offline

from pydantic import BaseSettings

class Settings(BaseSettings):
    """
    Loads MongoDB URI and database name from environment variables or defaults.
    Attributes:
        MONGO_URI (str): MongoDB connection string.
        DB_NAME (str): Name of the database.
    """
    MONGO_URI: str = "mongodb://localhost:27017"
    DB_NAME: str = "sign_language_glove"

    class Config:
        env_file = ".env"  # optionally load from .env file

settings = Settings()
