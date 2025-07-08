"""
Script for streaming real-time glove sensor data from a serial device to a WebSocket server.

- Reads data from a serial port (e.g., Arduino glove).
- Sends parsed sensor values as JSON to a WebSocket endpoint.
- Used for live data ingestion/testing, not required for main backend workflow unless live streaming is needed.
"""
# backend/streaming/glove_streamer.py
import serial
import asyncio
import websockets
import json

async def stream_data():
    """
    Read sensor data from serial port and stream it to a WebSocket server as JSON.
    Update the serial port and WebSocket URL as needed for your setup.
    """
    ser = serial.Serial('/dev/ttyUSB0', 9600)  # Update COM port as needed
    async with websockets.connect("ws://localhost:8000/ws/glove") as ws:
        while True:
            line = ser.readline().decode().strip()  # "0.1,0.2,..."
            values = list(map(float, line.split(',')))
            if len(values) == 11:
                data = {
                    "left": values[:5],
                    "right": values[5:10],
                    "imu": values[10],
                    "timestamp": asyncio.get_event_loop().time()
                }
                await ws.send(json.dumps(data))

asyncio.run(stream_data())
