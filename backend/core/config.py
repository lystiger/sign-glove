"""
Configuration file chứa các constants và settings
"""

# File paths
RAW_DATA = 'raw_data.csv' # Nhớ chỉnh đường dẫn nếu cần thiết
CLEAN_DATA = 'clean_data.csv'

NORMALIZE_NUMBER = 4095.0  # Chỉnh sửa tùy vào cảm biến sử dụng (ESP, Arduino)
DECIMAL_PLACES = 4  # Số chữ số thập phân cần làm tròn
FLEX_SENSORS = 5

# Noise reduction settings
WINDOW_SIZE = 3
THRESHOLD = 2.0

# Default noise reduction configuration
DEFAULT_NOISE_CONFIG = {
    'window_size': 3,           # Kích thước cửa sổ cho moving average và median
    'outlier_threshold': 2.0,   # Ngưỡng Z-score cho outlier detection
    'apply_moving_avg': True,   # Có áp dụng moving average không
    'apply_outlier': True,      # Có áp dụng outlier detection không
    'apply_median': False       # Có áp dụng median filter không
}