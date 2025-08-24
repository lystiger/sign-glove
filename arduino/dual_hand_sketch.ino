/*
  Dual-Hand Sign Glove Arduino Sketch
  -----------------------------------
  This code reads 5 flex sensors (one for each finger) and an MPU6050 IMU 
  for the second hand in a dual-hand sign glove system.
  
  Output format (same as first glove):
    flex1,flex2,flex3,flex4,flex5,accX,accY,accZ,gyroX,gyroY,gyroZ
  - flex1..flex5: Analog values from each flex sensor (fingers)
  - accX,accY,accZ: Accelerometer readings from MPU6050
  - gyroX,gyroY,gyroZ: Gyroscope readings from MPU6050

  Note: Use different serial port than the first glove
*/

#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

// Flex sensor pins (ESP32 ADC pins) - Use different pins than first glove
const int FLEX_PIN_1 = 25;  // Different from first glove (36)
const int FLEX_PIN_2 = 26;  // Different from first glove (34)
const int FLEX_PIN_3 = 27;  // Different from first glove (35)
const int FLEX_PIN_4 = 14;  // Different from first glove (32)
const int FLEX_PIN_5 = 12;  // Different from first glove (33)

// Optional: Add LED indicator for second glove
const int STATUS_LED = 2;

void setup() {
  Serial.begin(115200); // Start serial communication at 115200 baud
  Wire.begin();         // Initialize I2C
  
  // Setup LED
  pinMode(STATUS_LED, OUTPUT);
  digitalWrite(STATUS_LED, HIGH); // Turn on to indicate second glove is active

  mpu.initialize();     // Initialize MPU6050
  if (!mpu.testConnection()) {
    Serial.println("MPU6050 connection failed");
    digitalWrite(STATUS_LED, LOW); // Turn off LED if IMU fails
    while (1); // Halt if MPU6050 is not connected
  }
  Serial.println("MPU6050 connected - Second Hand Active");
  
  // Optional: print CSV header for reference
  Serial.println("flex1,flex2,flex3,flex4,flex5,accX,accY,accZ,gyroX,gyroY,gyroZ");
  
  // Blink LED to confirm setup
  for (int i = 0; i < 3; i++) {
    digitalWrite(STATUS_LED, LOW);
    delay(200);
    digitalWrite(STATUS_LED, HIGH);
    delay(200);
  }
}

void loop() {
  // --- Read flex sensors ---
  int flex1 = analogRead(FLEX_PIN_1);
  int flex2 = analogRead(FLEX_PIN_2);
  int flex3 = analogRead(FLEX_PIN_3);
  int flex4 = analogRead(FLEX_PIN_4);
  int flex5 = analogRead(FLEX_PIN_5);

  // --- Read MPU6050 accelerometer and gyroscope ---
  int16_t ax, ay, az, gx, gy, gz;
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  // --- Print all sensor data in CSV format ---
  Serial.print(flex1); Serial.print(",");
  Serial.print(flex2); Serial.print(",");
  Serial.print(flex3); Serial.print(",");
  Serial.print(flex4); Serial.print(",");
  Serial.print(flex5); Serial.print(",");
  Serial.print(ax); Serial.print(",");
  Serial.print(ay); Serial.print(",");
  Serial.print(az); Serial.print(",");
  Serial.print(gx); Serial.print(",");
  Serial.print(gy); Serial.print(",");
  Serial.println(gz);

  // Optional: Blink LED every 10 readings to show activity
  static int counter = 0;
  if (++counter % 10 == 0) {
    digitalWrite(STATUS_LED, !digitalRead(STATUS_LED));
  }

  delay(100);  // 10 Hz sampling rate (same as first glove)
} 