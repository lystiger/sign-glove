#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <MPU6050.h>

// ==================== WiFi CONFIG ====================
const char* ssid     = "SN186_3F";
const char* password = "16062023";

// ==================== WebSocket CONFIG ====================
const char* ws_host = "192.168.0.5";   // Your PC LAN IP
const uint16_t ws_port = 8000;
const char* ws_path = "/ws/predict";

WebSocketsClient webSocket;

// ==================== SENSOR CONFIG ====================
const int flexPins[5] = {34, 36, 35, 32, 33}; // 5 flex sensors
MPU6050 imu;

// Flex dynamic min/max for normalization
int flexMin[5] = {4095, 4095, 4095, 4095, 4095};
int flexMax[5] = {0, 0, 0, 0, 0};

// EMA smoothing constants
float alpha = 0.2;
float flexSmoothed[5] = {0};
float rollSmoothed = 0;
float pitchSmoothed = 0;
float yawSmoothed = 0;

// Gyro integration for yaw
float yaw = 0;
unsigned long lastTime = 0;

// ==================== Helpers ====================
float ema(float current, float previous) {
  return alpha * current + (1 - alpha) * previous;
}

void computeRollPitch(float ax, float ay, float az, float &roll, float &pitch) {
  roll  = atan2(ay, az) * 180.0 / PI;
  pitch = atan2(-ax, sqrt(ay * ay + az * az)) * 180.0 / PI;
}

// ==================== WebSocket Events ====================
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      Serial.println("[WSc] Disconnected");
      break;
    case WStype_CONNECTED:
      Serial.printf("[WSc] Connected to: %s\n", payload);
      break;
    case WStype_TEXT:
      Serial.printf("[WSc] Received text: %s\n", payload);
      break;
    case WStype_ERROR:
      Serial.println("[WSc] Error occurred");
      break;
  }
}

// ==================== Setup ====================
void setup() {
  Serial.begin(115200);
  Wire.begin();

  // Initialize flex pins
  for (int i = 0; i < 5; i++) pinMode(flexPins[i], INPUT);

  // Initialize IMU
  imu.initialize();
  if (!imu.testConnection()) {
    Serial.println("IMU connection failed");
  }

  // Connect WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  // Connect WebSocket
  webSocket.begin(ws_host, ws_port, ws_path);
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);

  lastTime = millis();
}

// ==================== Loop ====================
void loop() {
  webSocket.loop();

  unsigned long now = millis();
  float dt = (now - lastTime) / 1000.0; // delta time in seconds
  lastTime = now;

  if (webSocket.isConnected()) {
    StaticJsonDocument<512> doc;

    // ====== Build "right" object ======
    JsonObject right = doc.createNestedObject("right");
    JsonArray values = right.createNestedArray("values");

    // -------- Read Flex Sensors (5 values) --------
    for (int i = 0; i < 5; i++) {
      int raw = analogRead(flexPins[i]);
      if (raw < flexMin[i]) flexMin[i] = raw;
      if (raw > flexMax[i]) flexMax[i] = raw;

      float norm = (raw - flexMin[i]) / float(flexMax[i] - flexMin[i] + 1);
      flexSmoothed[i] = ema(norm, flexSmoothed[i]);
      values.add(flexSmoothed[i]);
    }

    // -------- Read IMU --------
    int16_t ax, ay, az, gx, gy, gz;
    imu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    float roll, pitch;
    computeRollPitch(float(ax), float(ay), float(az), roll, pitch);

    // Smooth roll/pitch/yaw
    rollSmoothed  = ema(roll / 180.0, rollSmoothed);
    pitchSmoothed = ema(pitch / 180.0, pitchSmoothed);
    float gz_dps = float(gz) / 131.0;
    yaw += gz_dps * dt;
    yawSmoothed = ema(yaw / 180.0, yawSmoothed);

    // -------- Add roll, pitch, yaw --------
    values.add(rollSmoothed);
    values.add(pitchSmoothed);
    values.add(yawSmoothed);

    // -------- Add gyro scaled (gx, gy, gz) --------
    values.add(float(gx) / 131.0 / 180.0);
    values.add(float(gy) / 131.0 / 180.0);
    values.add(float(gz) / 131.0 / 180.0);

    // Debug: check values count
    Serial.print("Values count: ");
    Serial.println(values.size());  // must be 11

    // -------- Timestamp --------
    right["timestamp"] = millis() / 1000.0;

    // -------- Language --------
    doc["language"] = "en";

    // Send JSON
    String jsonString;
    serializeJson(doc, jsonString);
    webSocket.sendTXT(jsonString);

    Serial.println("Sent: " + jsonString);
  }

  delay(50); // 20 Hz update rate
}
