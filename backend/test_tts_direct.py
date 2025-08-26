import asyncio
import websockets
import json
from services.tts_service import tts_service
from core.settings import settings

# Force using pyttsx3 for reliable offline TTS
settings.TTS_PROVIDER = "pyttsx3"

async def listen_and_speak():
    uri = "ws://localhost:8000/ws/predict"
    print(f"Connecting to WebSocket at {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected! Start making gestures with your glove...")
            print("(Press Ctrl+C to stop)")
            
            while True:
                try:
                    # Receive prediction
                    data = await websocket.recv()
                    prediction = json.loads(data)
                    gesture = prediction.get('gesture', '')
                    
                    if gesture and gesture != "Class 0":  # Skip "No Gesture"
                        print(f"Detected gesture: {gesture}")
                        await tts_service.speak_gesture(
                            gesture,
                            language="en",
                            play_on_esp32=False
                        )
                        
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed by server")
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    break
                    
    except Exception as e:
        print(f"Failed to connect to WebSocket: {e}")

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(listen_and_speak())
    except KeyboardInterrupt:
        print("\nStopped listening")