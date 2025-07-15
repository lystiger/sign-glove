"""
Simple and Effective Regularization Algorithms for Sensor Data Processing
Bao gồm 3 thuật toán đơn giản và hiệu quả:
1. Simple Kalman Filter - Lọc nhiễu tối ưu
2. Weighted Moving Average - Trung bình trọng số thích ứng
3. Exponential Smoothing - Làm mượt dữ liệu
"""

import logging
import csv
import os
import argparse
from collections import deque
from typing import List, Dict, Optional, Any

class RegularizationAlgorithms:
    """
    Class chứa 3 thuật toán regularization đơn giản và hiệu quả
    """
    
    def __init__(self, window_size: int = 5):
        """
        Khởi tạo các thuật toán regularization
        
        Args:
            window_size: Kích thước cửa sổ cho các thuật toán
        """
        self.window_size = window_size
        self.sensor_states = {}  # Lưu trạng thái cho từng sensor
        self.buffers = {}  # Buffer cho từng sensor
        
    def reset_states(self):
        """Reset tất cả trạng thái và buffer"""
        self.sensor_states.clear()
        self.buffers.clear()
        logging.info("All regularization states reset")

    # 1. SIMPLE KALMAN FILTER
    def simple_kalman_filter(self, measurement: float, sensor_id: str) -> float:
        """
        Thuật toán Kalman Filter đơn giản - Tối ưu cho real-time
        
        Args:
            measurement: Giá trị đo được hiện tại
            sensor_id: ID của sensor
            
        Returns:
            Giá trị đã được lọc
        """
        if sensor_id not in self.sensor_states:
            # Khởi tạo trạng thái ban đầu
            self.sensor_states[sensor_id] = {
                'estimate': measurement,  # Ước lượng hiện tại
                'error': 1.0,            # Sai số ước lượng
                'process_noise': 0.01,   # Noise của quá trình  
                'measurement_noise': 0.1  # Noise của phép đo
            }
            return measurement
        
        state = self.sensor_states[sensor_id]
        
        # Prediction step
        predicted_estimate = state['estimate']
        predicted_error = state['error'] + state['process_noise']
        
        # Update step
        kalman_gain = predicted_error / (predicted_error + state['measurement_noise'])
        
        # Cập nhật ước lượng
        state['estimate'] = predicted_estimate + kalman_gain * (measurement - predicted_estimate)
        state['error'] = (1 - kalman_gain) * predicted_error
        
        return state['estimate']

    # 2. WEIGHTED MOVING AVERAGE
    def weighted_moving_average(self, measurement: float, sensor_id: str) -> float:
        """
        Trung bình trọng số thích ứng - Đơn giản và hiệu quả
        
        Args:
            measurement: Giá trị đo được hiện tại
            sensor_id: ID của sensor
            
        Returns:
            Giá trị đã được lọc
        """
        buffer_key = f"wma_{sensor_id}"
        
        if buffer_key not in self.buffers:
            self.buffers[buffer_key] = deque(maxlen=self.window_size)
        
        buffer = self.buffers[buffer_key]
        buffer.append(measurement)
        
        if len(buffer) == 1:
            return measurement
        
        # Tạo trọng số tăng dần (giá trị mới có trọng số cao hơn)
        weights = []
        total_weight = 0
        
        for i in range(len(buffer)):
            weight = i + 1  # Trọng số tăng dần: 1, 2, 3, 4, 5
            weights.append(weight)
            total_weight += weight
        
        # Tính weighted average
        weighted_sum = sum(buffer[i] * weights[i] for i in range(len(buffer)))
        result = weighted_sum / total_weight
        
        return result

    # 3. EXPONENTIAL SMOOTHING
    def exponential_smoothing(self, measurement: float, sensor_id: str, 
                            alpha: float = 0.3) -> float:
        """
        Exponential Smoothing đơn giản - Responsive và smooth
        
        Args:
            measurement: Giá trị đo được hiện tại
            sensor_id: ID của sensor
            alpha: Hệ số smoothing (0 < alpha < 1)
            
        Returns:
            Giá trị đã được làm mượt
        """
        if sensor_id not in self.sensor_states:
            self.sensor_states[sensor_id] = {
                'smoothed_value': measurement
            }
            return measurement
        
        state = self.sensor_states[sensor_id]
        
        # Exponential smoothing formula
        state['smoothed_value'] = alpha * measurement + (1 - alpha) * state['smoothed_value']
        
        return state['smoothed_value']

    def apply_single_algorithm(self, data: List[float], algorithm: str = "kalman") -> List[float]:
        """
        Áp dụng một thuật toán cụ thể
        
        Args:
            data: Dữ liệu sensor cần xử lý
            algorithm: Thuật toán ("kalman", "weighted", "exponential")
            
        Returns:
            Dữ liệu đã được regularized
        """
        regularized_data = []
        
        for i, value in enumerate(data):
            sensor_id = f"sensor_{i}"
            
            if algorithm == "kalman":
                result = self.simple_kalman_filter(value, sensor_id)
            elif algorithm == "weighted":
                result = self.weighted_moving_average(value, sensor_id)
            elif algorithm == "exponential":
                result = self.exponential_smoothing(value, sensor_id)
            else:
                logging.warning(f"Unknown algorithm: {algorithm}, using kalman")
                result = self.simple_kalman_filter(value, sensor_id)
            
            regularized_data.append(result)
        
        return regularized_data

    def apply_combined_regularization(self, data: List[float], 
                                    algorithm_weights: Optional[Dict[str, float]] = None) -> List[float]:
        """
        Áp dụng kết hợp 3 thuật toán với trọng số
        
        Args:
            data: Dữ liệu sensor cần xử lý
            algorithm_weights: Trọng số cho từng thuật toán
                              {'kalman': 0.5, 'weighted': 0.3, 'exponential': 0.2}
                              
        Returns:
            Dữ liệu đã được regularized
        """
        if algorithm_weights is None:
            algorithm_weights = {
                'kalman': 0.5,
                'weighted': 0.3,
                'exponential': 0.2
            }
        
        # Normalize weights
        total_weight = sum(algorithm_weights.values())
        for key in algorithm_weights:
            algorithm_weights[key] /= total_weight
        
        regularized_data = []
        
        for i, value in enumerate(data):
            sensor_id = f"sensor_{i}"
            
            # Áp dụng từng thuật toán
            kalman_result = self.simple_kalman_filter(value, f"kalman_{sensor_id}")
            weighted_result = self.weighted_moving_average(value, f"weighted_{sensor_id}")
            exp_result = self.exponential_smoothing(value, f"exp_{sensor_id}")
            
            # Kết hợp kết quả theo trọng số
            combined_result = (algorithm_weights['kalman'] * kalman_result +
                             algorithm_weights['weighted'] * weighted_result +
                             algorithm_weights['exponential'] * exp_result)
            
            regularized_data.append(combined_result)
        
        return regularized_data

    def apply_adaptive_regularization(self, data: List[float]) -> List[float]:
        """
        Áp dụng regularization thích ứng - Tự động chọn thuật toán phù hợp
        Args:
            data: Dữ liệu sensor cần xử lý 
        Returns:
            Dữ liệu đã được regularized
        """
        if len(data) < 3:
            return data
        # Tính variance để đánh giá noise level
        variance = sum((x - sum(data)/len(data))**2 for x in data) / len(data)
        
        # Chọn thuật toán dựa trên variance
        if variance > 1.0:
            # Noise cao - dùng Kalman filter
            weights = {'kalman': 0.7, 'weighted': 0.2, 'exponential': 0.1}
        elif variance > 0.1:
            # Noise trung bình - dùng weighted average
            weights = {'kalman': 0.3, 'weighted': 0.5, 'exponential': 0.2}
        else:
            # Noise thấp - dùng exponential smoothing
            weights = {'kalman': 0.2, 'weighted': 0.3, 'exponential': 0.5}
        
        return self.apply_combined_regularization(data, weights)

    def get_algorithm_stats(self) -> Dict[str, Any]:
        """
        Lấy thống kê về hiệu suất của các thuật toán
        
        Returns:
            Dictionary chứa thông tin thống kê
        """
        stats = {
            'total_sensors': len(self.sensor_states),
            'active_buffers': len(self.buffers),
            'algorithms': {
                'kalman_states': len([k for k in self.sensor_states.keys() 
                                    if 'estimate' in self.sensor_states[k]]),
                'weighted_buffers': len([k for k in self.buffers.keys() 
                                       if k.startswith('wma_')]),
                'exponential_states': len([k for k in self.sensor_states.keys() 
                                         if 'smoothed_value' in self.sensor_states[k]])
            }
        }
        
        return stats

    def configure_algorithm(self, sensor_id: str, algorithm: str, params: Dict[str, Any]):
        """
        Cấu hình tham số cho thuật toán cụ thể
        
        Args:
            sensor_id: ID của sensor
            algorithm: Thuật toán ("kalman", "weighted", "exponential")
            params: Tham số cấu hình
        """
        if algorithm == "kalman" and sensor_id in self.sensor_states:
            state = self.sensor_states[sensor_id]
            if 'process_noise' in params:
                state['process_noise'] = params['process_noise']
            if 'measurement_noise' in params:
                state['measurement_noise'] = params['measurement_noise']
        
        elif algorithm == "weighted":
            if 'window_size' in params:
                buffer_key = f"wma_{sensor_id}"
                if buffer_key in self.buffers:
                    # Tạo lại buffer với window_size mới
                    old_data = list(self.buffers[buffer_key])
                    self.buffers[buffer_key] = deque(
                        old_data[-params['window_size']:], 
                        maxlen=params['window_size']
                    )
        
        logging.info(f"Configured {algorithm} for sensor {sensor_id} with params: {params}")

    def process_csv_file(self, input_path: str, output_path: str, method: str = "adaptive", 
                        window_size: int = 5) -> int:
        """
        Xử lý file CSV với regularization
        
        Args:
            input_path: Đường dẫn file input (raw_data.csv)
            output_path: Đường dẫn file output (clean_data.csv)
            method: Phương pháp regularization ("adaptive", "combined", "kalman", "weighted", "exponential")
            window_size: Kích thước cửa sổ
            
        Returns:
            Số dòng đã xử lý
        """
        if not os.path.exists(input_path):
            logging.error(f"Input file not found: {input_path}")
            return 0
        
        # Reset states for new file processing
        self.reset_states()
        
        row_count = 0
        
        try:
            with open(input_path, 'r', newline='', encoding='utf-8') as infile, \
                 open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                
                reader = csv.reader(infile)
                writer = csv.writer(outfile)
                
                # Read and write header
                try:
                    header = next(reader)
                    writer.writerow(header)
                except StopIteration:
                    logging.warning("Input file is empty")
                    return 0
                
                # Process each row
                for row in reader:
                    if len(row) < 3:  # Need at least session_id, label, and one sensor value
                        continue
                    
                    session_id, label, *sensor_values = row
                    
                    # Convert sensor values to float
                    try:
                        sensor_values = list(map(float, sensor_values[:11]))  # First 11 sensor values
                    except ValueError:
                        logging.warning(f"Skipping row {row_count + 1}: invalid sensor values")
                        continue
                    
                    # Apply regularization
                    if method == "adaptive":
                        regularized = self.apply_adaptive_regularization(sensor_values)
                    elif method == "combined":
                        regularized = self.apply_combined_regularization(sensor_values)
                    else:
                        regularized = self.apply_single_algorithm(sensor_values, method)
                    
                    # Write processed row
                    writer.writerow([session_id, label] + [round(val, 3) for val in regularized])
                    row_count += 1
                    
                    if row_count % 1000 == 0:
                        logging.info(f"Processed {row_count} rows...")
            
            logging.info(f"Successfully processed {row_count} rows from {input_path} to {output_path}")
            return row_count
            
        except Exception as e:
            logging.error(f"Error processing CSV file: {e}")
            return 0

# Hàm tiện ích để sử dụng
def create_regularizer(window_size: int = 5) -> RegularizationAlgorithms:
    """
    Tạo một instance của RegularizationAlgorithms
    Args:
        window_size: Kích thước cửa sổ   
    Returns:
        Instance của RegularizationAlgorithms
    """
    return RegularizationAlgorithms(window_size)

def main():
    """
    CLI interface để chọn phương pháp regularization
    """
    parser = argparse.ArgumentParser(description='Apply regularization algorithms to sensor data')
    parser.add_argument('--input', '-i', default='backend/data/raw_data.csv',
                       help='Input CSV file path (default: backend/data/raw_data.csv)')
    parser.add_argument('--output', '-o', default='backend/data/clean_data.csv',
                       help='Output CSV file path (default: backend/data/clean_data.csv)')
    parser.add_argument('--method', '-m', default='adaptive',
                       choices=['adaptive', 'combined', 'kalman', 'weighted', 'exponential'],
                       help='Regularization method (default: adaptive)')
    parser.add_argument('--window-size', '-w', type=int, default=5,
                       help='Window size for algorithms (default: 5)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create regularizer and process file
    regularizer = create_regularizer(args.window_size)
    
    print(f"Processing {args.input} with {args.method} method...")
    row_count = regularizer.process_csv_file(args.input, args.output, args.method, args.window_size)
    
    if row_count > 0:
        print(f"✅ Successfully processed {row_count} rows")
        print(f"📁 Output saved to: {args.output}")
    else:
        print("❌ No rows were processed")

# Example usage
if __name__ == "__main__":
    # Check if running as CLI
    import sys
    if len(sys.argv) > 1:
        main()
    else:
        # Run example tests
        # Tạo regularizer
        regularizer = create_regularizer(window_size=5)
        
        # Dữ liệu test với noise
        test_data = [1.0, 1.1, 5.0, 1.2, 0.9, 1.1, 1.0, 0.8, 1.2, 1.1]
        
        print("Original data:", test_data)
        
        # Test từng thuật toán
        print("\n=== Single Algorithm Tests ===")
        kalman_result = regularizer.apply_single_algorithm(test_data, "kalman")
        print("Kalman Filter:", [round(x, 3) for x in kalman_result])
        
        regularizer.reset_states()  # Reset để test thuật toán khác
        weighted_result = regularizer.apply_single_algorithm(test_data, "weighted")
        print("Weighted Moving Average:", [round(x, 3) for x in weighted_result])
        
        regularizer.reset_states()
        exp_result = regularizer.apply_single_algorithm(test_data, "exponential")
        print("Exponential Smoothing:", [round(x, 3) for x in exp_result])
        
        # Test combined regularization
        print("\n=== Combined Regularization ===")
        regularizer.reset_states()
        combined_result = regularizer.apply_combined_regularization(test_data)
        print("Combined Result:", [round(x, 3) for x in combined_result])
        
        # Test adaptive regularization
        print("\n=== Adaptive Regularization ===")
        regularizer.reset_states()
        adaptive_result = regularizer.apply_adaptive_regularization(test_data)
        print("Adaptive Result:", [round(x, 3) for x in adaptive_result])
        
        # Statistics
        print("\n=== Algorithm Stats ===")
        print("Stats:", regularizer.get_algorithm_stats())
        
        print("\n=== CLI Usage Examples ===")
        print("python regularization.py --method adaptive --input raw_data.csv --output clean_data.csv")
        print("python regularization.py -m kalman -i raw_data.csv -o clean_data.csv -w 10")
        print("python regularization.py --method combined --verbose")