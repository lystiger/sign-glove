/*
  Sign-Glove Arduino Sketch
  ------------------------
  This code reads 5 flex sensors (one for each finger) and an MPU6050 IMU (accelerometer + gyroscope)
  using an ESP32. It outputs the sensor values in CSV format over serial for use with the sign-glove project.

  Output format:
    flex1,flex2,flex3,flex4,flex5,accX,accY,accZ,gyroX,gyroY,gyroZ
  - flex1..flex5: Analog values from each flex sensor (fingers)
  - accX,accY,accZ: Accelerometer readings from MPU6050
  - gyroX,gyroY,gyroZ: Gyroscope readings from MPU6050

  The serial output is captured by a Python script for further processing and AI training.
*/

#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

// Flex sensor pins (ESP32 ADC pins)
const int FLEX_PIN_1 = 36;
const int FLEX_PIN_2 = 34;
const int FLEX_PIN_3 = 35;
const int FLEX_PIN_4 = 32;
const int FLEX_PIN_5 = 33;

void setup() {
  Serial.begin(115200); // Start serial communication at 115200 baud
  Wire.begin();         // Initialize I2C

  mpu.initialize();     // Initialize MPU6050
  if (!mpu.testConnection()) {
    Serial.println("MPU6050 connection failed");
    while (1); // Halt if MPU6050 is not connected
  }
  Serial.println("MPU6050 connected");

  // Optional: print CSV header for reference
  Serial.println("flex1,flex2,flex3,flex4,flex5,accX,accY,accZ,gyroX,gyroY,gyroZ");
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

  delay(100);  // 10 Hz sampling rate
}