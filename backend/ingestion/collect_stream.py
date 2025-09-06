import serial
import time
import asyncio
import json
import logging
import websockets
import sys, os
import csv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from processors import regularization
from core.settings import settings as app_settings

# ---------------- CONFIG ----------------
SERIAL_PORT = 'COM14'
BAUD_RATE = 115200
TOTAL_SENSORS = 11
MAX_QUEUE_SIZE = 20  # max frames queued before dropping old ones

RAW_CSV_PATH = "data/sensor_raw.csv"
REG_CSV_PATH = "data/sensor_regularized.csv"

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

# Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Regularizer
reg = regularization.create_regularizer(window_size=5)

# ---------------- HELPERS ----------------
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
        vals = [float(x) for x in line.split(',')]
        if len(vals) != TOTAL_SENSORS:
            return None
        return vals
    except Exception as e:
        logger.error(f"Read error: {e}")
        return None

def apply_regularization(values):
    fingers = values[:5]       # 5 flex sensors
    ax, ay, az = values[5:8]   # accelerometer
    gx, gy, gz = values[8:11]  # gyroscope

    fingers_reg = reg.apply_adaptive_regularization(fingers)
    roll, pitch, yaw = reg.imu_norm.process(ax, ay, az, gz)
    roll = reg.exponential_smoothing(roll, 'roll')
    pitch = reg.exponential_smoothing(pitch, 'pitch')
    yaw = reg.exponential_smoothing(yaw, 'yaw')
    gx_n, gy_n, gz_n = reg.imu_norm.normalize_gyro(gx, gy, gz)

    return fingers_reg, [ax, ay, az], [roll, pitch, yaw], [gx_n, gy_n, gz_n]

# ---------------- WEBSOCKET ----------------
async def send_to_backend(data_queue):
    ws_url = app_settings.BACKEND_BASE_URL.replace("http://","ws://").replace("https://","wss://") + "/ws/stream"
    logger.info(f"Connecting to WebSocket: {ws_url}")

    while True:
        try:
            async with websockets.connect(ws_url, ping_interval=20, ping_timeout=20) as ws:
                logger.info(f"Connected to WS: {ws_url}")
                while True:
                    if not data_queue:
                        await asyncio.sleep(0.01)
                        continue
                    data = data_queue.pop(0)
                    try:
                        await ws.send(json.dumps(data))
                    except Exception as e:
                        logger.warning(f"Send error, reconnecting: {e}")
                        break
                    await asyncio.sleep(0.005)
        except Exception as e:
            logger.warning(f"WebSocket reconnect in 2s: {e}")
            await asyncio.sleep(2)

# ---------------- MAIN LOOP ----------------
async def main():
    ser = connect_arduino()
    if not ser:
        return

    data_queue = []

    # Prepare CSV files
    first_run = not (os.path.exists(RAW_CSV_PATH) and os.path.exists(REG_CSV_PATH))
    with open(RAW_CSV_PATH, "a", newline="") as raw_file, \
         open(REG_CSV_PATH, "a", newline="") as reg_file:

        raw_writer = csv.writer(raw_file)
        reg_writer = csv.writer(reg_file)

        # Write headers if first run
        if first_run:
            raw_writer.writerow(["flex1","flex2","flex3","flex4","flex5","accX","accY","accZ","gyroX","gyroY","gyroZ","timestamp"])
            reg_writer.writerow(["finger1","finger2","finger3","finger4","finger5","accX","accY","accZ","roll","pitch","yaw","gx_n","gy_n","gz_n","timestamp"])

        ws_task = asyncio.create_task(send_to_backend(data_queue))
        logger.info("Starting live data collection...")

        try:
            while True:
                vals = read_sensor_data(ser)
                if vals:
                    timestamp = time.time()

                    # Log raw data
                    raw_writer.writerow(vals + [timestamp])
                    raw_file.flush()

                    # Regularize
                    fingers_reg, acc, imu_angles, gyro_norm = apply_regularization(vals)

                    # Log regularized data
                    reg_writer.writerow(fingers_reg + acc + imu_angles + gyro_norm + [timestamp])
                    reg_file.flush()

                    # Prepare payload for WebSocket
                    payload = {
                        "right": fingers_reg + acc + imu_angles + gyro_norm,  # 11 features
                        "timestamp": timestamp
                    }

                    if len(data_queue) >= MAX_QUEUE_SIZE:
                        data_queue.pop(0)
                    data_queue.append(payload)

                await asyncio.sleep(0.005)

        except KeyboardInterrupt:
            logger.info("Live collection stopped by user.")
        finally:
            if ser and ser.is_open:
                ser.close()
                logger.info("Serial connection closed.")
            ws_task.cancel()
            try:
                await ws_task
            except asyncio.CancelledError:
                pass

if __name__ == "__main__":
    asyncio.run(main())
