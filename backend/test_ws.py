import asyncio
import websockets
import json
import random

async def test_connection():
    uri = "ws://localhost:8000/ws/predict"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket server")
            
            # Test data with random sensor values
            test_data = {
                "right": {
                    "values": [random.uniform(0, 1000) for _ in range(11)],
                    "timestamp": 1234567890
                },
                "language": "en"
            }
            
            print("Sending test data:", test_data)
            await websocket.send(json.dumps(test_data))
            
            # Wait for response
            response = await websocket.recv()
            print("Received response:", response)
            
    except Exception as e:
        print(f"Error: {e}")

asyncio.get_event_loop().run_until_complete(test_connection())