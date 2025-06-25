'''
=====Note=====
 
'''
# Import những thư viện cần thiết
import csv
import os
import logging
from collections import deque
import statistics
import numpy as np
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RAW_DATA = 'raw.csv'
CLEAN_DATA = 'newcode.csv'
NORMALIZE_NUMBER = 4095.0 # Chỉnh sửa tùy vào cảm biến sử dụng (ESP, Arduino) 
DECIMAL_PLACES = 4 # Số chữ số thập phân cần làm tròn
FLEX_SENSORS = 5
WINDOW_SIZE = 3
THRESHOLD = 2.0
class NoiseReducer:
   """
   Class chứa các thuật toán noise reduction
   """
   # Khởi tạo các biến và giá trị mặc định
   def __init__(self, window_size=WINDOW_SIZE, outlier_threshold=THRESHOLD):
      self.window_size = window_size
      self.outlier_threshold = outlier_threshold
      self.sensor_buffers = {}  # Buffer cho từng sensor    
    
   def moving_average_window(self, data, id):
      """
      @effect: Áp dụng MAW filter
      @Args:
      sensor_data: Giá trị sensor hiện tại
      sensor_id: ID của sensor (để maintain buffer riêng biệt)
      @return: Giá trị sau khi áp dụng moving average
      """
      if id not in self.sensor_buffers:
         self.sensor_buffers[id] = deque(maxlen=self.window_size)
         buffer = self.sensor_buffers[id]
         buffer.append(data)
         return sum(buffer) / len(buffer) 
   
   def median_filter(self,data,id):
      '''
      @effect: Hàm áp dụng Median Filter
      @Args:
      data: Giá trị sensor hiện tại
      id: ID của sensor 
      @return: Giá trị median của các giá trị trong buffer
      '''
      buffer_key = f"median_{id}"
      if buffer_key not in self.sensor_buffers:
         self.sensor_buffers[buffer_key] = deque(maxlen=self.window_size)
        
      buffer = self.sensor_buffers[buffer_key]
      buffer.append(data)
        
      # Trả về median của các giá trị trong buffer
      return statistics.median(list(buffer))
    
   def outlier(self, data_list, threshold=None):
      """
      @effect: Detect và thay thế outliers bằng Z-score method
      @Args:
      data_list: List các giá trị cần kiểm tra outlier
      threshold: Ngưỡng Z-score (nếu None sẽ dùng self.outlier_threshold)
      @return: List đã được xử lý outliers
      """
      if threshold is None:
         threshold = self.outlier_threshold     
      if len(data_list) < 2:
         return data_list
      
      try:
         mean_val = statistics.mean(data_list)
         std_val = statistics.stdev(data_list)
         # Tránh chia cho 0
         if std_val == 0:
            return data_list 
         filtered_data = []
         
         for value in data_list:
            z_score = abs((value - mean_val) / std_val)
            if z_score > threshold:
               filtered_data.append(mean_val)
               logging.info(f"Outlier detected: {value} replaced with mean {mean_val}")
            else:
               filtered_data.append(value)
         return filtered_data
      except statistics.StatisticsError as e:
         logging.error("Error calculating statistics: {e}")
         return data_list
   
   def apply_filter(self, data, apply_MA=True, apply_median=True, apply_outlier=True):
      filtered_data = data.copy()
      # Áp dụng outlier detection trước (áp dụng cho toàn bộ row)
      if apply_outlier:
         filtered_data = self.outlier_detection_filter(filtered_data)
        
        # Áp dụng moving average hoặc median filter cho từng sensor
      if apply_MA or apply_median:
         for i in range(len(filtered_data)):
            if apply_MA:
               filtered_data[i] = self.moving_average_filter(filtered_data[i], f"sensor_{i}")
            elif apply_median:
               filtered_data[i] = self.median_filter(filtered_data[i], f"sensor_{i}")
        
      return filtered_data
   
   def reset_buffers(self):
      """
      @effect: Reset tất cả buffers (dùng khi bắt đầu xử lý file mới)
      """
      self.sensor_buffers.clear()
      logging.info("NoiseReducer buffers reset")
      
def normalize_data(values):
    '''
    @effect: Hàm để chuẩn hóa dữ liệu từ file CSV
    @Args: values: List chứa các giá trị cần chuẩn hóa
    @return : List chứa các giá trị đã chuẩn hóa
    @raise ZeroDivisionError: Nếu NORMALIZE_NUMBER là 0
    '''
    try:
        return [round(val / NORMALIZE_NUMBER, DECIMAL_PLACES) for val in values]
    except ZeroDivisionError as e:
        logging.warning(f"Error normalizing data: {e}")
        return values

def is_empty(row):
    '''
    @effect: Check dòng có rỗng hay không
    @Args: row: Dòng dữ liệu cần kiểm tra
    @return: True nếu dòng rỗng hoặc chỉ chứa khoảng trắng, False nếu có dữ liệu
    '''
    return not row or all(not cell.strip() for cell in row)

def row_validation(row,expected_col,row_num):
    '''
    @effect: Hàm kiểm tra dữ liệu trong mỗi dòng của file CSV
    @Args
    row: row dữ liệu cần kiểm tra
    expected_col: Số lượng cột 
    row_num: số thứ tự của dòng trong file CSV
    @return: Tuple chứa T/F và error msg
    '''
    # Kiểm tra nếu dòng rỗng 
    if is_empty(row):
        return False, f"Row {row_num} is empty."
    # Kiểm tra số lượng cột
    if len(row) != expected_col:
        return False, f"Row {row_num} has {len(row)} columns, expected {expected_col}!"
    # Kiểm tra nếu label trống
    if not row[-1].strip():
        return False, f"Row {row_num} has no label"
    # Kiểm tra cái cột dữ liệu check rỗng
    for i, cell in enumerate(row[:-1]): 
        if not cell.strip():
            return False, f"Row {row_num}, column {i+1} is empty."
    return True, "Valid row"

def read_data(file_path, use_noise_reduction=True, noise_config=None):
   '''
   @effect: Hàm đọc dữ liệu từ file raw_data.csv, gửi lại dữ liệu chuẩn bị ghi vào file clean_data.csv
   @Args: file_path: Đường dẫn đến file CSV cần đọc
   @return: Tuple chứa dữ liệu đã chuẩn hóa và header của file CSV
   @raise ValueError, IndexError: Nếu dữ liệu không hợp lệ hoặc không đủ cột
   @raise FileNotFoundError: Nếu file chưa được tạo
   '''
   skipped_rows = 0
   data = []
   header = [] 
   noise_reducer = None
   if noise_reducer:
         config = noise_config or {}
         window_size = config.get('window_size', 3)
         outlier_threshold = config.get('outlier_threshold', 2.0)
         noise_reducer = NoiseReducer(window_size=window_size, outlier_threshold=outlier_threshold)
         logging.info(f"NoiseReducer initialized with window_size={window_size} and outlier_threshold={outlier_threshold}")
   if not os.path.exists(file_path):
      raise FileNotFoundError(f"{file_path} not found!")
    
   try:
      with open(file_path, 'r', encoding='utf-8') as file:
         # 2 dòng này để loại dòng cuối
         lines = file.readlines()
         while lines and not lines[-1].strip():
            lines.pop()
            
            if not lines:
               raise ValueError(f"File {file_path} is empty.")
            reader = csv.reader(lines)
            
            try:
               header = next(reader)  # Đọc header
            except StopIteration:
               raise ValueError(f"File {file_path} is empty or has no header.")
            # Const chứa số cột của header
            expected_col = len(header)            
            for row_num, row in enumerate(reader, start=2):
               # Bỏ qua dòng cuối rỗng hoặc chỉ chứa whitespace
               if not row or all(not cell.strip() for cell in row):
                  continue
                
               # Kiểm tra tính hợp lệ của dòng
               is_valid, error_message = row_validation(row, expected_col, row_num)
               # Nếu !is_valid -> cảnh báo và bỏ qua data
               if not is_valid:
                  logging.warning(f" {error_message}")
                  skipped_rows += 1  
                  continue  # Skip dòng
               try:
                  values = [float(val.strip()) for val in row[:-1]]  # Chuyển đổi dữ liệu sang float và tránh label
                  label = row[-1].strip()  # Lấy label sang một bên
                  if noise_reducer:
                     # Có thể tùy chỉnh filter nào được áp dụng
                     apply_moving_avg = noise_config.get('apply_moving_avg', True) if noise_config else True
                     apply_outlier = noise_config.get('apply_outlier', True) if noise_config else True
                     apply_median = noise_config.get('apply_median', False) if noise_config else False
                        
                     values = noise_reducer.apply_filters(
                        values, 
                        apply_moving_avg=apply_moving_avg,
                        apply_outlier=apply_outlier,
                        apply_median=apply_median
                     )
                  data.append(values + [label])  # Thêm data và label vào dòng
               except (ValueError, IndexError) as e:
                  logging.warning(f"Warning: Row {row_num} has invalid data format: {e}")
                  skipped_rows += 1
                  continue  # Bỏ qua dòng nếu có lỗi                  
   except Exception as e:
      logging.warning(f"Error reading file {file_path}: {e}")
   print("==================== Result ====================")
   print(f"Successfully read {len(data)} rows, skipped {skipped_rows} invalid rows.")
   if use_noise_reduction:
      print("Noise reduction filters applied:")
      if noise_config:
         print(f"  - Moving Average: {noise_config.get('apply_moving_avg', True)}")
         print(f"  - Outlier Detection: {noise_config.get('apply_outlier', True)}")
         print(f"  - Median Filter: {noise_config.get('apply_median', False)}")
      else:
         print("  - Moving Average: True")
         print("  - Outlier Detection: True")
         print("  - Median Filter: False")
   # Trả về dữ liệu sau chuẩn hóa cùng header
   return data, header

def write_data(file_path, data, header):
    '''
    @effect: Hàm ghi dữ liệu đã chuẩn hóa vào file clean_data.csv
    @Args
    file_path: clean_data.csv
    data: Normalized data
    header: Header của file CSV
    @return: True nếu ghi thành công, False nếu không có dữ liệu
    '''
    if not data:
        logging.warning("No valid data to write!")
        return False
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(header) # Ghi header vào đầu file
            rows = 0
            for row in data:
                val = row[:-1]
                label = row[-1]
                normalized_data = normalize_data(val)  # Chuẩn hóa dữ liệu
                writer.writerow(normalized_data + [label])
                rows += 1
            # In ra số dòng ghi thành công
            logging.info(f"Total {rows} rows written to {file_path}.")
            return True
    except Exception as e:
        logging.warning(f"Error writing to file {file_path}: {e}")
        return False

def initialize_csv():
    '''
    @effect: Khởi tạo file CSV với header nếu file chưa tồn tại bỏ qua nếu đã có
    @return: True nếu thành công, False nếu có lỗi
    '''
    if os.path.exists(CLEAN_DATA):
        logging.info(f"File {CLEAN_DATA} already exists.")
        return True
    try:
        # Check thư mục nếu chưa tồn tại thì tạo
        os.makedirs(os.path.dirname(CLEAN_DATA) if os.path.dirname(CLEAN_DATA) else '.', exist_ok=True)
        
        with open(CLEAN_DATA, 'w', newline='', encoding='utf-8') as csvfile:        
            writer = csv.writer(csvfile)
            # Ghi header
            header = [f'flexSensor{i + 1}' for i in range(FLEX_SENSORS)] + ['label']
            writer.writerow(header)
        logging.info(f"File {CLEAN_DATA} created with header.")
        return True
    except Exception as e:
        logging.warning(f"Error creating file {CLEAN_DATA}: {e}")
        return False

def main():
   '''
   @effect: Hàm chính để đọc dữ liệu từ file raw_data.csv, chuẩn hóa và ghi vào file clean_data.csv
   '''    
   if not initialize_csv():
      logging.warning("Exiting.")
      return
   try:
      noise_config = {
         'window_size': 3,           # Kích thước cửa sổ cho moving average và median
         'outlier_threshold': 2.0,   # Ngưỡng Z-score cho outlier detection
         'apply_moving_avg': True,   # Có áp dụng moving average không
         'apply_outlier': True,      # Có áp dụng outlier detection không
         'apply_median': False
      }  
      new_data, header = read_data(RAW_DATA, use_noise_reduction=True, noise_config=noise_config)
      if not new_data:
         logging.warning("No valid data found in the input file.")
         return
      logging.info(f"Read {len(new_data)} valid rows from {RAW_DATA}.")
      if write_data(CLEAN_DATA, new_data, header):
         logging.info(f"Successfully wrote processed data into {CLEAN_DATA}.")
      else:
         logging.warning("Failed to write processed data.")
   except FileNotFoundError as e:
      logging.warning(f"File error: {e}")
   except Exception as e:
      logging.warning(f"Unexpected error: {e}")

if __name__ == "__main__":
   main()