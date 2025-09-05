import serial
import time
import asyncio
import threading
import json
import logging
from datetime import datetime
from collections import deque
import websockets

from processors import regularization
from core.settings import settings as app_settings

# ---------------- CONFIG ----------------
SERIAL_PORT = 'COM6'
BAUD_RATE = 115200
TOTAL_SENSORS = 11
SESSION_ID = "live_session"
LABEL = "live"

# Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Regularizer
reg = regularization.create_regularizer(window_size=5)

# ---------------- HELPER ----------------
def connect_arduino():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        ser.reset_input_buffer()
        logger.info(f"Connected to Arduino on {SERIAL_PORT}")
        return ser
    except Exception as e:
        logger.error(f"Failed to connect: {e}")
        return None

def read_sensor_data(ser):
    try:
        line = ser.readline().decode('utf-8').strip()
        if not line:
            return None
        vals = list(map(float, line.split(',')))
        if len(vals) != TOTAL_SENSORS:
            return None
        return vals
    except Exception as e:
        logger.error(f"Read error: {e}")
        return None

def apply_regularization(values):
    # Split values
    flex = values[:5]
    ax, ay, az = values[5:8]
    gx, gy, gz = values[8:11]

    # Flex regularization
    flex_reg = reg.apply_adaptive_regularization(flex)

    # IMU angles
    roll, pitch, yaw = reg.imu_norm.process(ax, ay, az, gz)

    # Exponential smoothing on angles
    roll = reg.exponential_smoothing(roll, 'roll')
    pitch = reg.exponential_smoothing(pitch, 'pitch')
    yaw = reg.exponential_smoothing(yaw, 'yaw')

    # Gyro normalization
    gx_n, gy_n, gz_n = reg.imu_norm.normalize_gyro(gx, gy, gz)

    return flex_reg + [roll, pitch, yaw, gx_n, gy_n, gz_n]

# ---------------- WEBSOCKET ----------------
async def send_to_backend(data_queue):
    ws_url = app_settings.BACKEND_BASE_URL.replace("http://","ws://").replace("https://","wss://") + "/ws/predict"
    try:
        async with websockets.connect(ws_url) as ws:
            logger.info(f"Connected to WS: {ws_url}")
            while True:
                if not data_queue:
                    await asyncio.sleep(0.02)
                    continue
                data = data_queue.pop(0)
                await ws.send(json.dumps(data))
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

# ---------------- MAIN LOOP ----------------
def main():
    ser = connect_arduino()
    if not ser:
        return

    data_queue = []
    loop = asyncio.get_event_loop()
    threading.Thread(target=loop.run_until_complete, args=(send_to_backend(data_queue),), daemon=True).start()

    logger.info("Starting live data collection...")

    try:
        while True:
            vals = read_sensor_data(ser)
            if vals:
                reg_vals = apply_regularization(vals)
                payload = {
                    "left": reg_vals[:5],
                    "right": reg_vals[5:8],
                    "imu": reg_vals[8:11],
                    "timestamp": time.time()
                }
                data_queue.append(payload)
            time.sleep(0.005)

    except KeyboardInterrupt:
        logger.info("Live collection stopped by user.")
    finally:
        if ser and ser.is_open:
            ser.close()
            logger.info("Serial connection closed.")

if __name__ == "__main__":
    main()
