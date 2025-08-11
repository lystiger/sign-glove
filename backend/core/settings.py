"""
Centralized settings for the sign glove system.
Loads all configuration from environment variables or defaults.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Dict, Any, Optional
import os

class Settings(BaseSettings):
    # Database
    MONGO_URI: str = Field("mongodb://localhost:27017", env="MONGO_URI")
    DB_NAME: str = Field("sign_language_glove", env="DB_NAME")

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

settings = Settings()
