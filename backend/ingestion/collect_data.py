'''
------------------IMPORT NOTES------------------
 - nhớ pip install -r requirements.txt (nó sẽ tải full thư viện cho ae)
 - khi chạy code nhớ kết nối Arduino với máy tính và mở cổng serial
'''
# Thêm các thư viện cần thiết
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

# Backend imports
sys.path.append('.')  
from core.database import sensor_collection

# Thông số cấu hình 
SERIAL_PORT = 'COM3'  # Nhớ đổi tùy vào máy nhưng thường là COM3 
BAUD_RATE = 115200  # Baud rate cho ESP32
FILE_PATH = 'raw_data.csv'
LABEL = ''  # Thêm label sau, hiện tại để trống
FLEX_SENSORS = 11
LOG_FILE = 'data_collection.log'

# Setup logging properly
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)

def connect_arduino():
    '''
    @effect: Kết nối với Arduino qua cổng serial
    @return: Serial object nếu kết nối thành công, None nếu không
    '''
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Đợi Arduino reset
        logger.info(f"Connected to {SERIAL_PORT} successfully!") 
        ser.flushInput()
        return ser
    except Exception as e:
        logger.error(f"Failed to connect to serial port: {e}")  
        return None

def read_data(ser):
    '''
    @effect: Đọc dữ liệu từ Arduino và trả về giá trị dưới dạng list
    - nếu không đọc được dữ liệu thì trả về None
    - hàm sẽ có 1 preprocess nhỏ là đảm bảo đủ 11 giá trị dữ liệu từ Arduino nếu không sẽ bỏ qua
    @parameter ser: Serial object
    @return: list dữ liệu đọc được từ Arduino hoặc None nếu không đọc được
    '''
    try:
        line = ser.readline().decode('utf-8').strip()  
        if line:
            val = line.split(',')
            if len(val) != FLEX_SENSORS:
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
    '''
    @effect: Khởi tạo file CSV với header nếu file chưa tồn tại bỏ qua nếu đã có
    @return: True nếu thành công, False nếu có lỗi
    '''
    file_exists = os.path.exists(FILE_PATH)
    
    if not file_exists:
        try:
            os.makedirs(os.path.dirname(FILE_PATH) if os.path.dirname(FILE_PATH) else '.', exist_ok=True)
            with open(FILE_PATH, 'w', newline='') as csvfile:        
                writer = csv.writer(csvfile)
                header = [f'flexSensor{i + 1}' for i in range(FLEX_SENSORS)] + ['label']
                writer.writerow(header)
            logger.info(f"File {FILE_PATH} created with header.")  
            return True
        except Exception as e:
            logger.error(f"Error creating file {FILE_PATH}: {e}")  
            return False
    else:
        logger.info(f"File {FILE_PATH} already exists.")  
        return True

async def send_to_backend(data_queue):
    '''
    @effect: Gửi dữ liệu từ hàng đợi lên WebSocket của backend để dự đoán real-time
    @note: chỉ gửi nếu có dữ liệu trong hàng đợi
    '''
    try:
        async with websockets.connect("ws://localhost:8080/ws/predict") as ws:
            logger.info("WebSocket connection to backend established.")
            while True:
                if not data_queue:
                    await asyncio.sleep(0.05)
                    continue
                data = data_queue.pop(0)
                await ws.send(json.dumps(data))
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

def main():
    '''
    @effect: Hàm chính để kết nối với cổng serial, ghi dữ liệu vào CSV, và gửi WebSocket
    @note: Nhớ check kết nối Arduino trước khi chạy
    - ghi 11 giá trị dữ liệu và nhãn vào file CSV
    - gửi dữ liệu realtime đến backend WebSocket
    - ấn Ctrl + C để dừng chương trình
    '''
    print("===============Starting data collection process===============")  
    
    if not initialize_csv():
        logger.error("Failed to initialize CSV file")  
        return
    
    ser = connect_arduino()
    if ser is None:
        logger.error("Failed to connect to Arduino.")  
        return

    data_queue = []

    # Chạy thread gửi dữ liệu song song với ghi CSV
    loop = asyncio.get_event_loop()
    threading.Thread(target=loop.run_until_complete, args=(send_to_backend(data_queue),), daemon=True).start()

    try:
        with open(FILE_PATH, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            log = 0
            while True:
                data = read_data(ser)
                if data:
                    row = data + [LABEL]
                    writer.writerow(row)
                    csvfile.flush()

                    # Chuẩn bị dữ liệu gửi qua WebSocket
                    ws_payload = {
                        "left": data[:5],
                        "right": data[5:10],
                        "imu": data[10],
                        "timestamp": time.time()
                    }
                    data_queue.append(ws_payload)

                    log += 1
                    if log % 10 == 0:
                        logger.info(f"Logged {log} rows and streamed to backend.")  
                time.sleep(0.01)    
    except PermissionError:
        logger.error(f"Permission denied: Cannot write to {FILE_PATH}") 
    except KeyboardInterrupt:
        logger.info("Stopped by user.")
        try:
            logger.info("Triggering model training via backend...")
            response = requests.post("http://localhost:8080/training")
            if response.status_code == 200:
                logger.info("Training triggered successfully.")
            else:
                logger.error(f"Training trigger failed: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error triggering training: {e}")  
    except FileNotFoundError:
        logger.error(f"Could not open file {FILE_PATH} for writing.")  
    finally:
        if ser and ser.is_open:
            ser.close()
            logger.info("End serial connection.")  

if __name__ == "__main__":
    main()
