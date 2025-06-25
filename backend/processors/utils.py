"""
    Chứa các hàm dùng cho xử lí dữ liệu hoặc validation
"""
import logging
from core.config import NORMALIZE_NUMBER, DECIMAL_PLACES

def normalize_data(values):
    """
    @effect: Hàm để chuẩn hóa dữ liệu từ file CSV
    @Args: values: List chứa các giá trị cần chuẩn hóa
    @return: List chứa các giá trị đã chuẩn hóa
    @raise ZeroDivisionError: Nếu NORMALIZE_NUMBER là 0
    """
    try:
        return [round(val / NORMALIZE_NUMBER, DECIMAL_PLACES) for val in values]
    except ZeroDivisionError as e:
        logging.warning(f"Error normalizing data: {e}")
        return values

def is_empty(row):
    """
    @effect: Check dòng có rỗng hay không
    @Args: row: Dòng dữ liệu cần kiểm tra
    @return: True nếu dòng rỗng hoặc chỉ chứa khoảng trắng, False nếu có dữ liệu
    """
    return not row or all(not cell.strip() for cell in row)

def row_validation(row, expected_col, row_num):
    """
    @effect: Hàm kiểm tra dữ liệu trong mỗi dòng của file CSV
    @Args:
        row: row dữ liệu cần kiểm tra
        expected_col: Số lượng cột 
        row_num: số thứ tự của dòng trong file CSV
    @return: Tuple chứa T/F và error msg
    """
    # Kiểm tra nếu dòng rỗng 
    if is_empty(row):
        return False, f"Row {row_num} is empty."
    
    # Kiểm tra số lượng cột
    if len(row) != expected_col:
        return False, f"Row {row_num} has {len(row)} columns, expected {expected_col}!"
    
    # Kiểm tra nếu label trống
    if not row[-1].strip():
        return False, f"Row {row_num} has no label"
    
    # Kiểm tra các cột dữ liệu có rỗng không
    for i, cell in enumerate(row[:-1]): 
        if not cell.strip():
            return False, f"Row {row_num}, column {i+1} is empty."
    
    return True, "Valid row"