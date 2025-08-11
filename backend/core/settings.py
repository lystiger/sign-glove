"""
Centralized settings for the sign glove system.
Loads all configuration from environment variables or defaults.
"""
from pydantic_settings import BaseSettings
<<<<<<< HEAD
from pydantic import Field, validator
=======
from pydantic import Field
>>>>>>> 9de1e983acf572c97ba2cb123b7d2f0bd6cc1985
from typing import List, Dict, Any, Optional
import os
from pathlib import Path
from pydantic_settings import SettingsConfigDict

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    DEBUG: bool = Field(False, env="DEBUG")
    
    # Security
    JWT_SECRET_KEY: str = Field("your-secret-key-change-in-production", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Database
    MONGO_URI: str = Field("mongodb://localhost:27017", env="MONGO_URI")
    DB_NAME: str = Field("sign_glove", env="DB_NAME")
    
    # Model/data paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, 'data')
    AI_DIR: str = os.path.join(BASE_DIR, 'AI')
    RAW_DATA_PATH: str = os.path.join(DATA_DIR, 'raw_data.csv')
    CLEAN_DATA_PATH: str = os.path.join(DATA_DIR, 'clean_data.csv')
    GESTURE_DATA_PATH: str = os.path.join(DATA_DIR, 'gesture_data.csv')
    MODEL_PATH: str = os.path.join(AI_DIR, 'gesture_model.tflite')
    MODEL_DUAL_PATH: str = os.path.join(AI_DIR, 'gesture_model_dual.tflite')
    METRICS_PATH: str = os.path.join(AI_DIR, 'training_metrics.json')
    RESULTS_DIR: str = os.path.join(AI_DIR, 'results')
    
    # CORS
    CORS_ORIGINS: List[str] = Field(["http://localhost:5173"], env="CORS_ORIGINS")
    
    # TTS config
    TTS_ENABLED: bool = Field(True, env="TTS_ENABLED")
    TTS_PROVIDER: str = Field("edge", env="TTS_PROVIDER")
    TTS_VOICE: str = Field("ur-IN-SalmanNeural", env="TTS_VOICE")
    TTS_RATE: int = Field(150, env="TTS_RATE")
    TTS_VOLUME: float = Field(2.0, env="TTS_VOLUME")
    TTS_CACHE_ENABLED: bool = Field(True, env="TTS_CACHE_ENABLED")
    TTS_CACHE_DIR: str = Field("tts_cache", env="TTS_CACHE_DIR")
    
    # ESP32 config
    ESP32_IP: str = Field("192.168.1.123", env="ESP32_IP")
    
    # Sensor/processing constants
    FLEX_SENSORS: int = 5
    IMU_SENSORS: int = 6
    TOTAL_SENSORS: int = FLEX_SENSORS + IMU_SENSORS
    NORMALIZE_NUMBER: float = 4095.0
    DECIMAL_PLACES: int = 4
    WINDOW_SIZE: int = 3
    OUTLIER_THRESHOLD: float = 2.0
    DEFAULT_NOISE_CONFIG: Dict[str, Any] = {
        'window_size': 3,
        'outlier_threshold': 2.0,
        'apply_moving_avg': True,
        'apply_outlier': True,
        'apply_median': False
    }
    
    # Performance and monitoring
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field("logs/app.log", env="LOG_FILE")
    MAX_REQUEST_SIZE: int = Field(10 * 1024 * 1024, env="MAX_REQUEST_SIZE")  # 10MB
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(60, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
    
    # API configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Sign Glove AI"
    VERSION: str = "1.0.0"
    
    # File upload settings
    UPLOAD_DIR: str = Field("uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(50 * 1024 * 1024, env="MAX_FILE_SIZE")  # 50MB
    ALLOWED_FILE_TYPES: List[str] = Field([".csv", ".json", ".txt"], env="ALLOWED_FILE_TYPES")
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_FILE_TYPES", pre=True)
    def parse_allowed_file_types(cls, v):
        if isinstance(v, str):
            return [file_type.strip() for file_type in v.split(",")]
        return v
    
    @validator("JWT_SECRET_KEY")
    def validate_jwt_secret_key(cls, v):
        if v == "your-secret-key-change-in-production" and os.getenv("ENVIRONMENT") == "production":
            raise ValueError("JWT_SECRET_KEY must be set in production")
        return v

<<<<<<< HEAD
    @validator("DB_NAME", pre=True)
    def pick_db_name(cls, v):
        # Support both DB_NAME and DATABASE_NAME
        if v and isinstance(v, str) and v.strip():
            return v
        alt = os.getenv("DATABASE_NAME")
        return alt or "sign_glove"
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"
    
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.ENVIRONMENT.lower() == "testing"
    
    # pydantic v2 settings configuration
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore',  # ignore unknown env keys like DATABASE_NAME
    )
=======
    # Auth/JWT settings
    SECRET_KEY: str = Field("change-me-in-prod", env="SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    COOKIE_SECURE: bool = Field(False, env="COOKIE_SECURE")

    # Optional default editor seed
    DEFAULT_EDITOR_EMAIL: Optional[str] = Field(None, env="DEFAULT_EDITOR_EMAIL")
    DEFAULT_EDITOR_PASSWORD: Optional[str] = Field(None, env="DEFAULT_EDITOR_PASSWORD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
>>>>>>> 9de1e983acf572c97ba2cb123b7d2f0bd6cc1985

# Create settings instance
settings = Settings()

# Ensure required directories exist
def ensure_directories():
    """Create required directories if they don't exist."""
    directories = [
        settings.DATA_DIR,
        settings.AI_DIR,
        settings.RESULTS_DIR,
        os.path.dirname(settings.LOG_FILE),
        settings.UPLOAD_DIR,
        settings.TTS_CACHE_DIR
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

# Initialize directories
ensure_directories()
