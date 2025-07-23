"""
    TTS Service
"""
import asyncio
import os
import logging
import hashlib
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional
from core.settings import settings

# TTS Libraries Import Check
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False
try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False
try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

# Gesture mapping
GESTURE_MAPPING = {
    "Class 0": "",
    "Class 1": "", 
    "Class 2": "",
    "Class 3": "",
    "Class 4": "",
    "Class 5": "",
    "Class 6": "",
    "Class 7": "",
    "Class 8": "",
    "Class 9": "",
    "Class 10": "",
}

class TTSService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.cache = {}
        self.pyttsx3_engine = None
        # Ensure cache dir exists
        if settings.TTS_CACHE_ENABLED and not os.path.exists(settings.TTS_CACHE_DIR):
            os.makedirs(settings.TTS_CACHE_DIR)
        if HAS_PYTTSX3:
            self._init_pyttsx3()

    def _init_pyttsx3(self):
        try:
            self.pyttsx3_engine = pyttsx3.init()
            self.pyttsx3_engine.setProperty('rate', settings.TTS_RATE)
            self.pyttsx3_engine.setProperty('volume', settings.TTS_VOLUME)
        except Exception as e:
            logging.error(f"Failed to initialize pyttsx3: {e}")

    def get_cache_path(self, text, voice):
        text_hash = hashlib.md5(f"{text}_{voice}".encode()).hexdigest()
        return os.path.join(settings.TTS_CACHE_DIR, f"{text_hash}.mp3")

    async def speak(self, text: str, voice: str = None):
        if not settings.TTS_ENABLED:
            return {"status": "disabled"}
        provider = settings.TTS_PROVIDER
        try:
            if provider == "edge" and HAS_EDGE_TTS:
                return await self._speak_edge(text, voice)
            elif provider == "gtts" and HAS_GTTS:
                return await self._speak_gtts(text)
            elif provider == "pyttsx3" and HAS_PYTTSX3:
                return await self._speak_pyttsx3(text)
            else:
                return {"status": "error", "message": "No TTS provider available"}
        except Exception as e:
            logging.error(f"TTS error: {e}")
            return {"status": "error", "message": str(e)}

    async def _speak_edge(self, text, voice: str = None):
        voice = voice or settings.TTS_VOICE
        cache_path = self.get_cache_path(text, voice)
        if settings.TTS_CACHE_ENABLED and os.path.exists(cache_path):
            return {"status": "success", "provider": "edge", "audio_path": cache_path}
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(cache_path)
        return {"status": "success", "provider": "edge", "audio_path": cache_path}

    async def _speak_gtts(self, text: str):
        cache_path = self.get_cache_path(text, "vi")
        if settings.TTS_CACHE_ENABLED and os.path.exists(cache_path):
            return {"status": "success", "provider": "gtts", "audio_path": cache_path}
        tts = gTTS(text=text, lang="vi")
        tts.save(cache_path)
        return {"status": "success", "provider": "gtts", "audio_path": cache_path}

    async def _speak_pyttsx3(self, text: str):
        if not self.pyttsx3_engine:
            return {"status": "error", "message": "pyttsx3 not available"}
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(self.executor, self._pyttsx3_speak, text)
        return {"status": "success" if success else "error", "provider": "pyttsx3"}

    def _pyttsx3_speak(self, text):
        try:
            self.pyttsx3_engine.say(text)
            self.pyttsx3_engine.runAndWait()
            return True
        except:
            return False

    def get_gesture_text(self, label):
        return GESTURE_MAPPING.get(label, label)

    def get_config(self):
        return {
            "config": {
                "provider": settings.TTS_PROVIDER,
                "voice": settings.TTS_VOICE,
                "rate": settings.TTS_RATE,
                "volume": settings.TTS_VOLUME,
                "cache_enabled": settings.TTS_CACHE_ENABLED,
                "cache_dir": settings.TTS_CACHE_DIR
            },
            "available_providers": {
                "pyttsx3": HAS_PYTTSX3,
                "gtts": HAS_GTTS,
                "edge_tts": HAS_EDGE_TTS
            },
            "gesture_mapping": GESTURE_MAPPING
        }

    def update_config(self, config: dict):
        # This method can be expanded to update settings dynamically if needed
        pass

    def cleanup(self):
        self.executor.shutdown(wait=False)

tts_service = TTSService()