'''
=====Note=====
 - File này không dùng noise filter, có thể dùng thử train model nhưng cần so sánh dữ liệu test
'''
# Import những thư viện cần thiết
import csv
import os
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RAW_DATA = 'raw.csv'
CLEAN_DATA = 'clean_data.csv'
NORMALIZE_NUMBER = 4095.0 # Chỉnh sửa tùy vào cảm biến sử dụng (ESP, Arduino) 
DECIMAL_PLACES = 4 # Số chữ số thập phân cần làm tròn
FLEX_SENSORS = 5

def normalize_data(values):
    '''
    @effect: Hàm để chuẩn hóa dữ liệu 
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

def read_data(file_path):
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
                    data.append(values + [label])  # Thêm data và label vào dòng
                except (ValueError, IndexError) as e:
                    logging.warning(f"Warning: Row {row_num} has invalid data format: {e}")
                    skipped_rows += 1
                    continue  # Bỏ qua dòng nếu có lỗi                  
    except Exception as e:
        logging.warning(f"Error reading file {file_path}: {e}")
    print("==================== Result ====================")
    print(f"Successfully read {len(data)} rows, skipped {skipped_rows} invalid rows.")
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
        new_data, header = read_data(RAW_DATA)
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