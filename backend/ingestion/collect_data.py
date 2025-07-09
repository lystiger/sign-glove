# ------------------IMPORT NOTES------------------
# - pip install -r requirements.txt
# - Kết nối Arduino và mở đúng cổng serial

import serial
import time
import csv
import os
import logging
import sys
import uuid
import asyncio
import threading
import websockets
import json
import requests
from datetime import datetime

# Backend imports
sys.path.append('.')
from core.database import sensor_collection  # MongoDB collection

# ========= CONFIG =========
SERIAL_PORT = 'COM8'  # 👈 Change to your port (e.g., /dev/ttyUSB0)
BAUD_RATE = 115200
FLEX_SENSORS = 5
ACCEL_SENSORS = 3
GYRO_SENSORS = 3
TOTAL_SENSORS = FLEX_SENSORS + ACCEL_SENSORS + GYRO_SENSORS
LABEL = 'A'  # 👈 Set this before collecting
SESSION_ID = str(uuid.uuid4())
CSV_DIR = 'data'
RAW_DATA_PATH = f"{CSV_DIR}/raw_data.csv"
FILE_PATH = f"{CSV_DIR}/{LABEL}_{SESSION_ID}.csv"
LOG_FILE = 'data_collection.log'

# ========= Logging setup =========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def connect_arduino():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        logger.info(f"Connected to {SERIAL_PORT} successfully!")
        ser.reset_input_buffer()
        return ser
    except Exception as e:
        logger.error(f"Failed to connect to serial port: {e}")
        return None


def read_data(ser):
    try:
        line = ser.readline().decode('utf-8').strip()
        if line:
            val = line.split(',')
            if len(val) != TOTAL_SENSORS:
                return None
            try:
                val = list(map(int, val))
                logger.info(f"[SUCCESS] Read values: {val}")
                return val
            except ValueError:
                return None
    except Exception as e:
        logger.error(f"Error reading data: {e}")
    return None


def initialize_csv():
    try:
        os.makedirs(CSV_DIR, exist_ok=True)
        if not os.path.exists(RAW_DATA_PATH):
            with open(RAW_DATA_PATH, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                header = ['session_id', 'label', 'flex1', 'flex2', 'flex3', 'flex4', 'flex5', 'accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']
                writer.writerow(header)
            logger.info(f"CSV file created: {RAW_DATA_PATH}")
        return True
    except Exception as e:
        logger.error(f"Error creating CSV: {e}")
        return False


async def send_to_backend(data_queue):
    try:
        async with websockets.connect("ws://localhost:8080/ws/predict") as ws:
            logger.info("WebSocket connected.")
            while True:
                if not data_queue:
                    await asyncio.sleep(0.05)
                    continue
                data = data_queue.pop(0)
                await ws.send(json.dumps(data))
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


def main():
    print("=============== Starting Data Collection ===============")

    if not initialize_csv():
        return

    ser = connect_arduino()
    if ser is None:
        return

    data_queue = []
    loop = asyncio.get_event_loop()
    threading.Thread(target=loop.run_until_complete, args=(send_to_backend(data_queue),), daemon=True).start()

    try:
        with open(RAW_DATA_PATH, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            log = 0

            while True:
                data = read_data(ser)
                if data:
                    row = [SESSION_ID, LABEL] + data[:5] + data[5:8] + data[8:11]
                    writer.writerow(row)
                    csvfile.flush()

                    # Save to MongoDB
                    mongo_doc = {
                        "session_id": SESSION_ID,
                        "label": LABEL,
                        "timestamp": datetime.utcnow(),
                        "values": data
                    }
                    sensor_collection.insert_one(mongo_doc)

                    # Send to WebSocket
                    ws_payload = {
                        "flex": data[:5],                 # 5 flex values
                        "accel": data[5:8],               # accelX, Y, Z
                        "gyro": data[8:11],
                        "timestamp": time.time()
                    }
                    data_queue.append(ws_payload)

                    log += 1
                    if log % 10 == 0:
                        logger.info(f"Logged {log} rows to CSV and MongoDB.")

                time.sleep(0.01)

    except PermissionError:
        logger.error(f"Permission denied for {RAW_DATA_PATH}")
    except KeyboardInterrupt:
        logger.info("Stopped by user.")
        try:
            logger.info("Triggering model training...")
            response = requests.post("http://localhost:8080/training/trigger")
            if response.status_code == 200:
                logger.info("Training triggered successfully.")
            else:
                logger.error(f"Training trigger failed: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error triggering training: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()
            logger.info("Serial connection closed.")


if __name__ == "__main__":
    main()
