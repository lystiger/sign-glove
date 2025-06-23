"""
Main application file
"""
import logging
from config import RAW_DATA, CLEAN_DATA, DEFAULT_NOISE_CONFIG
from data_processor import read_data, write_data, initialize_csv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    @effect: Hàm chính để đọc dữ liệu từ file raw_data.csv, chuẩn hóa và ghi vào file clean_data.csv
    """    
    if not initialize_csv(CLEAN_DATA):
        logging.error("Failed to initialize CSV file. Exiting.")
        return
    
    try:
        # Sử dụng config mặc định hoặc có thể tùy chỉnh
        noise_config = DEFAULT_NOISE_CONFIG.copy()
        
        # Đọc và xử lý dữ liệu
        new_data, header = read_data(RAW_DATA, use_noise_reduction=True, noise_config=noise_config)
        
        if not new_data:
            logging.warning("No valid data found in the input file.")
            return
        
        logging.info(f"Read {len(new_data)} valid rows from {RAW_DATA}.")
        
        # Ghi dữ liệu đã xử lý
        if write_data(CLEAN_DATA, new_data, header):
            logging.info(f"Successfully wrote processed data into {CLEAN_DATA}.")
        else:
            logging.error("Failed to write processed data.")
            
    except FileNotFoundError as e:
        logging.error(f"File error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()