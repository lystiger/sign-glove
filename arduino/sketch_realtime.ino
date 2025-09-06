/*
  Optimized Sign-Glove Arduino Sketch
  -----------------------------------
  Reads 5 flex sensors and an MPU6050 IMU using an ESP32.
  Outputs CSV to serial for real-time gesture prediction.
*/

#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

// Flex sensor pins (ESP32 ADC pins)
const int FLEX_PINS[5] = {36, 34, 35, 32, 33};
const int NUM_FLEX = 5;

// Sampling rate (ms)
const unsigned long SAMPLE_INTERVAL = 100; // 10 Hz
unsigned long lastSampleTime = 0;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  
  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("MPU6050 connection failed");
    while (1); // Halt if MPU6050 is not connected
  }
  Serial.println("MPU6050 connected");

  // Optional: CSV header
  Serial.println("flex1,flex2,flex3,flex4,flex5,accX,accY,accZ,gyroX,gyroY,gyroZ,timestamp");
}

void loop() {
  unsigned long now = millis();
  if (now - lastSampleTime < SAMPLE_INTERVAL) return;
  lastSampleTime = now;

  // --- Read flex sensors ---
  int flex[NUM_FLEX];
  for (int i = 0; i < NUM_FLEX; i++) {
    flex[i] = analogRead(FLEX_PINS[i]);
  }

  // --- Read MPU6050 accelerometer and gyroscope ---
  int16_t ax, ay, az, gx, gy, gz;
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  // --- Print CSV line ---
  for (int i = 0; i < NUM_FLEX; i++) {
    Serial.print(flex[i]);
    Serial.print(",");
  }
  Serial.print(ax); Serial.print(",");
  Serial.print(ay); Serial.print(",");
  Serial.print(az); Serial.print(",");
  Serial.print(gx); Serial.print(",");
  Serial.print(gy); Serial.print(",");
  Serial.print(gz); Serial.print(",");
  Serial.println(now); // timestamp
}
