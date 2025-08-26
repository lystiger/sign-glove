# Voice Data Collection for Real-time Streaming
# Captures audio from microphone and streams to backend via WebSocket

import asyncio
import websockets
import json
import logging
import pyaudio
import numpy as np
import time
import threading
from datetime import datetime
import os
import sys

# Backend imports
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from core.settings import settings

# ========= AUDIO CONFIG =========
CHUNK = 1024  # Audio chunk size
FORMAT = pyaudio.paInt16  # 16-bit audio
CHANNELS = 1  # Mono audio
RATE = 16000  # Sample rate (16kHz for speech recognition)
RECORD_SECONDS = 0.5  # Duration of each audio chunk
SILENCE_THRESHOLD = 500  # Silence detection threshold
MIN_SPEECH_DURATION = 1.0  # Minimum speech duration to process

# ========= Logging setup =========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voice_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VoiceStreamer:
    def __init__(self):
        self.audio = None
        self.stream = None
        self.is_recording = False
        self.audio_queue = []
        self.websocket = None
        
    def initialize_audio(self):
        """Initialize PyAudio for microphone capture"""
        try:
            self.audio = pyaudio.PyAudio()
            
            # List available audio devices
            logger.info("Available audio devices:")
            for i in range(self.audio.get_device_count()):
                info = self.audio.get_device_info_by_index(i)
                logger.info(f"  {i}: {info['name']} - {info['maxInputChannels']} input channels")
            
            # Open audio stream
            self.stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                stream_callback=self.audio_callback
            )
            
            logger.info(f"Audio stream initialized: {RATE}Hz, {CHANNELS} channel(s)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize audio: {e}")
            return False
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Callback function for audio stream"""
        if self.is_recording:
            audio_data = np.frombuffer(in_data, dtype=np.int16)
            
            # Check if audio contains speech (simple volume-based detection)
            volume = np.sqrt(np.mean(audio_data**2))
            
            if volume > SILENCE_THRESHOLD:
                self.audio_queue.append({
                    'audio_data': audio_data.tolist(),
                    'timestamp': time.time(),
                    'volume': float(volume),
                    'sample_rate': RATE,
                    'channels': CHANNELS
                })
        
        return (in_data, pyaudio.paContinue)
    
    def start_recording(self):
        """Start audio recording"""
        if not self.stream:
            logger.error("Audio stream not initialized")
            return False
            
        self.is_recording = True
        self.stream.start_stream()
        logger.info("Voice recording started")
        return True
    
    def stop_recording(self):
        """Stop audio recording"""
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
        logger.info("Voice recording stopped")
    
    async def connect_websocket(self):
        """Connect to backend WebSocket for voice streaming"""
        try:
            ws_url = settings.BACKEND_BASE_URL.replace("http://", "ws://").replace("https://", "wss://") + "/ws/voice"
            self.websocket = await websockets.connect(ws_url)
            logger.info(f"WebSocket connected to {ws_url}")
            return True
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            return False
    
    async def stream_audio(self):
        """Stream audio data to backend via WebSocket"""
        if not self.websocket:
            logger.error("WebSocket not connected")
            return
            
        try:
            while self.is_recording:
                if self.audio_queue:
                    audio_chunk = self.audio_queue.pop(0)
                    
                    # Prepare payload
                    payload = {
                        'type': 'voice_data',
                        'audio_data': audio_chunk['audio_data'],
                        'timestamp': audio_chunk['timestamp'],
                        'volume': audio_chunk['volume'],
                        'sample_rate': audio_chunk['sample_rate'],
                        'channels': audio_chunk['channels'],
                        'chunk_size': len(audio_chunk['audio_data'])
                    }
                    
                    await self.websocket.send(json.dumps(payload))
                    logger.debug(f"Sent audio chunk: {len(audio_chunk['audio_data'])} samples, volume: {audio_chunk['volume']:.2f}")
                
                await asyncio.sleep(0.01)  # Small delay to prevent overwhelming
                
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error streaming audio: {e}")
    
    async def listen_for_responses(self):
        """Listen for responses from backend (voice recognition results)"""
        if not self.websocket:
            return
            
        try:
            async for message in self.websocket:
                try:
                    response = json.loads(message)
                    
                    if response.get('type') == 'voice_recognition':
                        text = response.get('text', '')
                        confidence = response.get('confidence', 0)
                        logger.info(f"Voice Recognition: '{text}' (confidence: {confidence:.2f})")
                        
                    elif response.get('type') == 'error':
                        logger.error(f"Backend error: {response.get('message', 'Unknown error')}")
                        
                    elif response.get('type') == 'status':
                        logger.info(f"Backend status: {response.get('message', 'No message')}")
                        
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON response: {message}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed by server")
        except Exception as e:
            logger.error(f"Error listening for responses: {e}")
    
    def cleanup(self):
        """Clean up audio resources"""
        self.stop_recording()
        
        if self.stream:
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        
        logger.info("Audio resources cleaned up")

async def main():
    """Main function to run voice streaming"""
    streamer = VoiceStreamer()
    
    try:
        # Initialize audio
        if not streamer.initialize_audio():
            logger.error("Failed to initialize audio system")
            return
        
        # Connect to WebSocket
        if not await streamer.connect_websocket():
            logger.error("Failed to connect to WebSocket")
            return
        
        # Start recording
        if not streamer.start_recording():
            logger.error("Failed to start recording")
            return
        
        logger.info("Voice streaming started. Press Ctrl+C to stop.")
        
        # Run streaming and listening tasks concurrently
        await asyncio.gather(
            streamer.stream_audio(),
            streamer.listen_for_responses()
        )
        
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        streamer.cleanup()

if __name__ == "__main__":
    # Check if required dependencies are available
    try:
        import pyaudio
        import numpy as np
        import websockets
    except ImportError as e:
        logger.error(f"Missing required dependency: {e}")
        logger.error("Please install: pip install pyaudio numpy websockets")
        sys.exit(1)
    
    asyncio.run(main())
