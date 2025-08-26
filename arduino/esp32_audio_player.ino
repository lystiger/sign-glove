#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>

// WiFi credentials - Update these!
const char* ssid = "P901";
const char* password = "98765321";

// WebSocket server details
const char* ws_host = "116.111.97.116"; // Your computer's IP where backend runs
const uint16_t ws_port = 8000;
const char* ws_path = "/ws/predict";

WebSocketsClient webSocket;

// Sensor pins - adjust based on your setup
const int sensorPins[] = {34, 36, 35, 32, 33}; // Example pins
const int numSensors = 5;

void setup() {
  Serial.begin(115200);
  
  // Initialize sensor pins as inputs
  for (int i = 0; i < numSensors; i++) {
    pinMode(sensorPins[i], INPUT);
  }
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi");
  
  // Initialize WebSocket
  webSocket.begin(ws_host, ws_port, ws_path);
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000); // Try reconnecting every 5s if connection is lost
}

void loop() {
  webSocket.loop();
  
  if (webSocket.isConnected()) {
    // Read sensor values
    StaticJsonDocument<200> doc;
    JsonArray left = doc.createNestedArray("left");
    
    // Read all sensor values
    for (int i = 0; i < numSensors; i++) {
      left.add(analogRead(sensorPins[i]) / 4095.0); // Convert to 0-1 range
    }
    
    // Add right hand data (if available, otherwise use zeros)
    JsonArray right = doc.createNestedArray("right");
    for (int i = 0; i < numSensors; i++) {
      right.add(0.0); // Add your right hand sensor values here if available
    }
    
    doc["language"] = "en";
    
    // Send data as JSON string
    String jsonString;
    serializeJson(doc, jsonString);
    webSocket.sendTXT(jsonString);
  }
  
  delay(100); // Adjust delay as needed (ms)
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      Serial.printf("[WSc] Disconnected!\n");
      break;
    case WStype_CONNECTED:
      Serial.printf("[WSc] Connected to: %s\n", payload);
      break;
    case WStype_TEXT:
      Serial.printf("[WSc] Received text: %s\n", payload);
      break;
  }
}