"""
Noise reduction algorithms và filters
"""
import logging
import statistics
from collections import deque
from backend.core.config import WINDOW_SIZE, THRESHOLD

class NoiseReducer:
    """
    Class chứa các thuật toán noise reduction
    """
    
    def __init__(self, window_size=WINDOW_SIZE, outlier_threshold=THRESHOLD):
        """Khởi tạo các biến và giá trị mặc định"""
        self.window_size = window_size
        self.outlier_threshold = outlier_threshold
        self.sensor_buffers = {}  # Buffer cho từng sensor    
    
    def moving_average_window(self, data, id):
        """
        @effect: Áp dụng MAW filter
        @Args:
            data: Giá trị sensor hiện tại
            id: ID của sensor (để maintain buffer riêng biệt)
        @return: Giá trị sau khi áp dụng moving average
        """
        if id not in self.sensor_buffers:
            self.sensor_buffers[id] = deque(maxlen=self.window_size)
        
        buffer = self.sensor_buffers[id]
        buffer.append(data)
        return sum(buffer) / len(buffer) 
   
    def median_filter(self, data, id):
        """
        @effect: Hàm áp dụng Median Filter
        @Args:
            data: Giá trị sensor hiện tại
            id: ID của sensor 
        @return: Giá trị median của các giá trị trong buffer
        """
        buffer_key = f"median_{id}"
        if buffer_key not in self.sensor_buffers:
            self.sensor_buffers[buffer_key] = deque(maxlen=self.window_size)
        
        buffer = self.sensor_buffers[buffer_key]
        buffer.append(data)
        
        # Trả về median của các giá trị trong buffer
        return statistics.median(list(buffer))
    
    def outlier_detection(self, data_list, threshold=None):
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
            logging.error(f"Error calculating statistics: {e}")
            return data_list
   
    def apply_filters(self, data, apply_moving_avg=True, apply_median=False, apply_outlier=True):
        """
        @effect: Áp dụng các filter theo cấu hình
        @Args:
            data: Dữ liệu cần filter
            apply_moving_avg: Có áp dụng moving average không
            apply_median: Có áp dụng median filter không  
            apply_outlier: Có áp dụng outlier detection không
        @return: Dữ liệu đã được filter
        """
        filtered_data = data.copy()
        
        # Áp dụng outlier detection trước (áp dụng cho toàn bộ row)
        if apply_outlier:
            filtered_data = self.outlier_detection(filtered_data)
        
        # Áp dụng moving average hoặc median filter cho từng sensor
        if apply_moving_avg or apply_median:
            for i in range(len(filtered_data)):
                if apply_moving_avg:
                    filtered_data[i] = self.moving_average_window(filtered_data[i], f"sensor_{i}")
                elif apply_median:
                    filtered_data[i] = self.median_filter(filtered_data[i], f"sensor_{i}")
        
        return filtered_data
   
    def reset_buffers(self):
        """
        @effect: Reset tất cả buffers (dùng khi bắt đầu xử lý file mới)
        """
        self.sensor_buffers.clear()
        logging.info("NoiseReducer buffers reset")