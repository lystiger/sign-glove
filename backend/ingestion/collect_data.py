'''
------------------IMPORT NOTES------------------
 - nhớ pip install -r requirements.txt(nó sẽ tải full thư viện cho ae)
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

# Backend imports
sys.path.append('.')  
from backend.core.database import sensor_collection


# Thông số cấu hình 
SERIAL_PORT = 'COM3' # Nhớ đổi tùy vào máy nhưng thường là COM3 
BAUD_RATE = 115200 # Baud rate cho ESP32
FILE_PATH = 'raw_data.csv'
LABEL = '' # Thêm label sau, hiện tại để trống
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
        time.sleep(2)  # Wait for Arduino to reset
        logger.info(f"Connected to {SERIAL_PORT} successfully!") 
        ser.flushInput()
        return ser
    except Exception as e:
        logger.error(f"Failed to connect to serial port: {e}")  
        return None
    
def read_data(ser):
    '''
    @effect: đọc dữ liệu từ Arduino và trả về giá trị dưới dạng list
    - nếu không đọc được dữ liệu thì trả về None
    - hàm sẽ có 1 preprocess nhỏ là đảm bảo đủ 5 giá trị dữ liệu từ Arduino nếu không sẽ bỏ qua
    @parameter ser: Serial object
    @return: list dữ liệu đọc được từ Arduino hoặc None nếu không đọc được
    '''
    try:
        line = ser.readline().decode('utf-8').strip()  
        if line:
            val = line.split(',')
            if len(val) != FLEX_SENSORS: #Kiểm tra số lượng cột 
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
    @return: True nếu thành công, False nếu có lỗi  # FIX: Added return type documentation
    '''
    file_exists = os.path.exists(FILE_PATH)
    
    if not file_exists:
        try:
            # Check thư mục nếu chưa tồn tại thì tạo
            os.makedirs(os.path.dirname(FILE_PATH) if os.path.dirname(FILE_PATH) else '.', exist_ok=True)
            
            with open(FILE_PATH, 'w', newline='') as csvfile:        
                writer = csv.writer(csvfile)
                # Ghi header
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

def main():
    '''
    @effect: Hàm chính để kết nối với cổng serial và ghi dữ liệu vào file CSV
    @note: Nhớ check kết nối Arduino trước khi chạy
    - ghi 5 giá trị dữ liệu và nhãn vào file CSV (hiện tại nhãn để trống)
    - ấn Ctrl + C để dừng chương trình
    - sẽ báo lỗi nếu không thể mở cổng serial hoặc không có file để ghi dữ liệu, sửa lại FILE_PATH 
    '''
    print("===============Starting data collection process===============")  
    
    if not initialize_csv():
        logger.error("Failed to initialize CSV file")  
        return
    
    # Kết nối với Arduino
    ser = connect_arduino()
    if ser is None:
        logger.error("Failed to connect to Arduino.")  
        return
    
    try:
        with open(FILE_PATH, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            log = 0
            while True:
                data = read_data(ser)
                if data:
                    row = data + [LABEL]
                    writer.writerow(row)
                    csvfile.flush() # Đảm bảo ghi dữ liệu ngay lập tức thay vì đợi buffer đầy
                    log += 1
                    if log % 10 == 0:
                        logger.info(f"Logged {log} rows of data has been written to {FILE_PATH}.")  
                time.sleep(0.01)    
    except PermissionError:
        logger.error(f"Permission denied: Cannot write to {FILE_PATH}") 
    #Chương trình sẽ dừng khi ấn Ctrl+C hoặc stop từ terminal
    except KeyboardInterrupt:
        logger.info("Stopped by user.")  
    except FileNotFoundError:
        logger.error(f"Could not open file {FILE_PATH} for writing.")  
    finally:
        if ser and ser.is_open:
            ser.close()
            logger.info("End serial connection.")  

if __name__ == "__main__":
    main()