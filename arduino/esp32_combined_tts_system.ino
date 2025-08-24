#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <SD.h>
#include <SPI.h>
#include <ArduinoJson.h>
#include "Audio.h"

// WiFi credentials
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

// SD Card pins for ESP32
#define SD_CS_PIN 5
#define SD_MOSI_PIN 23
#define SD_MISO_PIN 19
#define SD_SCK_PIN 18

// Audio pins (I2S)
#define I2S_DOUT 25
#define I2S_BCLK 27
#define I2S_LRC 26

// Sensor pins (for gesture data streaming)
#define FLEX_1 36
#define FLEX_2 39
#define FLEX_3 34
#define FLEX_4 35
#define FLEX_5 32

// Control pins
#define STATUS_LED 2
#define SPEAKER_CTRL_PIN 4
#define VOLUME_PIN 33

AsyncWebServer server(80);
Audio audio;

// System configuration
const String TTS_BASE_PATH = "/tts/";
String currentLanguage = "en";
bool audioEnabled = true;
int currentVolume = 15;
bool sensorStreamingEnabled = false;

// Gesture mappings
struct GestureMapping {
  String gestureClass;
  String filename;
  String text;
};

GestureMapping gestureMappings[] = {
  {"Class 0", "hello.mp3", "Hello"},
  {"Class 1", "yes.mp3", "Yes"},
  {"Class 2", "no.mp3", "No"},
  {"Class 3", "thankyou.mp3", "Thank you"},
  {"Class 4", "please.mp3", "Please"},
  {"Class 5", "sorry.mp3", "Sorry"},
  {"Class 6", "goodbye.mp3", "Goodbye"},
  {"Class 7", "help.mp3", "Help"},
  {"Class 8", "water.mp3", "Water"},
  {"Class 9", "food.mp3", "Food"},
  {"Class 10", "emergency.mp3", "Emergency"}
};
const int NUM_GESTURES = 11;

void setup() {
  Serial.begin(115200);
  
  // Initialize pins
  pinMode(STATUS_LED, OUTPUT);
  pinMode(SPEAKER_CTRL_PIN, OUTPUT);
  pinMode(VOLUME_PIN, INPUT);
  
  // Initialize sensor pins
  pinMode(FLEX_1, INPUT);
  pinMode(FLEX_2, INPUT);
  pinMode(FLEX_3, INPUT);
  pinMode(FLEX_4, INPUT);
  pinMode(FLEX_5, INPUT);
  
  digitalWrite(STATUS_LED, LOW);
  digitalWrite(SPEAKER_CTRL_PIN, HIGH);
  
  Serial.println("ESP32 Combined TTS System Starting...");
  
  // Initialize SD card
  if (!initializeSDCard()) {
    Serial.println("[ERROR] SD Card initialization failed!");
    blinkError();
    return;
  }
  
  // Initialize Audio
  audio.setPinout(I2S_BCLK, I2S_LRC, I2S_DOUT);
  audio.setVolume(currentVolume);
  
  // Connect to WiFi
  if (!connectToWiFi()) {
    Serial.println("[ERROR] WiFi connection failed!");
    blinkError();
    return;
  }
  
  // Create TTS folder structure
  createTTSFolderStructure();
  
  // Setup web server
  setupWebServerRoutes();
  server.begin();
  
  Serial.println("ESP32 Combined TTS System Ready!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  digitalWrite(STATUS_LED, HIGH);
  
  // Play welcome message
  playWelcomeMessage();
}

bool initializeSDCard() {
  Serial.println("Initializing 32GB SD card...");
  
  SPI.begin(SD_SCK_PIN, SD_MISO_PIN, SD_MOSI_PIN, SD_CS_PIN);
  
  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("SD card initialization failed!");
    return false;
  }
  
  uint8_t cardType = SD.cardType();
  if (cardType == CARD_NONE) {
    Serial.println("No SD card attached");
    return false;
  }
  
  uint64_t cardSize = SD.cardSize() / (1024 * 1024);
  Serial.printf("SD Card Size: %lluMB\n", cardSize);
  
  if (cardSize < 30000) {
    Serial.println("Warning: SD card smaller than expected (32GB)");
  }
  
  return true;
}

bool connectToWiFi() {
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  
  unsigned long startTime = millis();
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    
    if (millis() - startTime > 20000) {
      return false;
    }
  }
  
  Serial.println("\nWiFi connected!");
  return true;
}

void createTTSFolderStructure() {
  Serial.println("Creating TTS folder structure on 32GB SD card...");
  
  // Create base TTS folder
  if (!SD.exists(TTS_BASE_PATH)) {
    SD.mkdir(TTS_BASE_PATH);
    Serial.println("Created /tts/ folder");
  }
  
  // Create language folders
  String languages[] = {"en", "vn", "fr"};
  for (int i = 0; i < 3; i++) {
    String langPath = TTS_BASE_PATH + languages[i];
    if (!SD.exists(langPath)) {
      SD.mkdir(langPath);
      Serial.println("Created " + langPath + " folder");
    }
  }
}

void setupWebServerRoutes() {
  // System health and status
  server.on("/health", HTTP_GET, [](AsyncWebServerRequest *request){
    StaticJsonDocument<400> response;
    response["status"] = "ok";
    response["device"] = "ESP32 Combined TTS System";
    response["language"] = currentLanguage;
    response["volume"] = currentVolume;
    response["audio_enabled"] = audioEnabled;
    response["sensor_streaming"] = sensorStreamingEnabled;
    response["free_space"] = SD.totalBytes() - SD.usedBytes();
    response["total_space"] = SD.totalBytes();
    response["wifi_rssi"] = WiFi.RSSI();
    
    String responseString;
    serializeJson(response, responseString);
    request->send(200, "application/json", responseString);
  });
  
  // Upload audio files from backend
  server.on("/upload_audio", HTTP_POST, 
    [](AsyncWebServerRequest *request) {
      // Upload complete handler
    },
    [](AsyncWebServerRequest *request, String filename, size_t index, uint8_t *data, size_t len, bool final) {
      handleFileUpload(request, filename, index, data, len, final);
    }
  );
  
  // Play gesture audio (called by backend after prediction)
  server.on("/play_gesture", HTTP_POST, [](AsyncWebServerRequest *request){
    if (!request->hasParam("gesture", true)) {
      request->send(400, "text/plain", "Missing gesture parameter");
      return;
    }
    
    String gesture = request->getParam("gesture", true)->value();
    String language = currentLanguage;
    
    if (request->hasParam("language", true)) {
      language = request->getParam("language", true)->value();
    }
    
    bool success = playGestureAudio(gesture, language);
    
    StaticJsonDocument<200> response;
    response["status"] = success ? "success" : "error";
    response["gesture"] = gesture;
    response["language"] = language;
    response["file_played"] = getGestureFilename(gesture);
    
    String responseString;
    serializeJson(response, responseString);
    request->send(success ? 200 : 500, "application/json", responseString);
  });
  
  // Language management
  server.on("/set_language", HTTP_POST, [](AsyncWebServerRequest *request){
    if (!request->hasParam("language", true)) {
      request->send(400, "text/plain", "Missing language parameter");
      return;
    }
    
    String newLanguage = request->getParam("language", true)->value();
    String langPath = TTS_BASE_PATH + newLanguage;
    
    if (!SD.exists(langPath)) {
      request->send(400, "text/plain", "Language folder not found");
      return;
    }
    
    currentLanguage = newLanguage;
    Serial.println("Language changed to: " + currentLanguage);
    
    StaticJsonDocument<100> response;
    response["status"] = "success";
    response["language"] = currentLanguage;
    
    String responseString;
    serializeJson(response, responseString);
    request->send(200, "application/json", responseString);
  });
  
  // Audio control
  server.on("/set_volume", HTTP_POST, [](AsyncWebServerRequest *request){
    if (!request->hasParam("volume", true)) {
      request->send(400, "text/plain", "Missing volume parameter");
      return;
    }
    
    int newVolume = request->getParam("volume", true)->value().toInt();
    if (newVolume < 0 || newVolume > 21) {
      request->send(400, "text/plain", "Volume must be 0-21");
      return;
    }
    
    currentVolume = newVolume;
    audio.setVolume(currentVolume);
    
    request->send(200, "text/plain", "Volume set to " + String(currentVolume));
  });
  
  server.on("/speaker/on", HTTP_POST, [](AsyncWebServerRequest *request){
    digitalWrite(SPEAKER_CTRL_PIN, HIGH);
    audioEnabled = true;
    Serial.println("Speaker turned ON");
    request->send(200, "text/plain", "Speaker ON");
  });
  
  server.on("/speaker/off", HTTP_POST, [](AsyncWebServerRequest *request){
    digitalWrite(SPEAKER_CTRL_PIN, LOW);
    audioEnabled = false;
    audio.stopSong();
    Serial.println("Speaker turned OFF");
    request->send(200, "text/plain", "Speaker OFF");
  });
  
  // File management
  server.on("/list_files", HTTP_GET, [](AsyncWebServerRequest *request){
    String language = currentLanguage;
    if (request->hasParam("language")) {
      language = request->getParam("language")->value();
    }
    
    StaticJsonDocument<1024> response;
    JsonArray files = response.createNestedArray("files");
    
    String langPath = TTS_BASE_PATH + language;
    File dir = SD.open(langPath);
    if (dir && dir.isDirectory()) {
      File file = dir.openNextFile();
      while (file) {
        if (!file.isDirectory() && String(file.name()).endsWith(".mp3")) {
          JsonObject fileObj = files.createNestedObject();
          fileObj["name"] = String(file.name());
          fileObj["size"] = file.size();
          fileObj["path"] = langPath + "/" + String(file.name());
        }
        file = dir.openNextFile();
      }
    }
    dir.close();
    
    String responseString;
    serializeJson(response, responseString);
    request->send(200, "application/json", responseString);
  });
  
  // Sensor streaming control
  server.on("/sensor/start", HTTP_POST, [](AsyncWebServerRequest *request){
    sensorStreamingEnabled = true;
    Serial.println("Sensor streaming started");
    request->send(200, "text/plain", "Sensor streaming started");
  });
  
  server.on("/sensor/stop", HTTP_POST, [](AsyncWebServerRequest *request){
    sensorStreamingEnabled = false;
    Serial.println("Sensor streaming stopped");
    request->send(200, "text/plain", "Sensor streaming stopped");
  });
}

void handleFileUpload(AsyncWebServerRequest *request, String filename, size_t index, uint8_t *data, size_t len, bool final) {
  static File uploadFile;
  static String currentFilePath;
  
  String language = "en";
  if (request->hasParam("language")) {
    language = request->getParam("language")->value();
  }
  
  if (index == 0) {
    currentFilePath = TTS_BASE_PATH + language + "/" + filename;
    Serial.println("Starting upload: " + currentFilePath);
    
    uploadFile = SD.open(currentFilePath, FILE_WRITE);
    if (!uploadFile) {
      Serial.println("Failed to open file for writing");
      request->send(500, "text/plain", "Failed to create file");
      return;
    }
  }
  
  if (uploadFile && len > 0) {
    size_t written = uploadFile.write(data, len);
    if (written != len) {
      Serial.printf("Write error: %d/%d bytes written\n", written, len);
    }
  }
  
  if (final) {
    if (uploadFile) {
      uploadFile.close();
      Serial.println("Upload completed: " + currentFilePath);
      
      StaticJsonDocument<200> response;
      response["status"] = "success";
      response["file_path"] = currentFilePath;
      response["language"] = language;
      response["size"] = SD.open(currentFilePath).size();
      
      String responseString;
      serializeJson(response, responseString);
      request->send(200, "application/json", responseString);
      
      blinkSuccess();
    } else {
      request->send(500, "text/plain", "Upload failed");
      blinkError();
    }
  }
}

bool playGestureAudio(String gestureClass, String language) {
  if (!audioEnabled) {
    Serial.println("Audio disabled");
    return false;
  }
  
  String filename = getGestureFilename(gestureClass);
  if (filename == "") {
    Serial.println("Unknown gesture: " + gestureClass);
    return false;
  }
  
  String filePath = TTS_BASE_PATH + language + "/" + filename;
  
  if (!SD.exists(filePath)) {
    Serial.println("Audio file not found: " + filePath);
    return false;
  }
  
  audio.stopSong();
  Serial.println("Playing: " + filePath);
  return audio.connecttoSD(filePath.c_str());
}

String getGestureFilename(String gestureClass) {
  for (int i = 0; i < NUM_GESTURES; i++) {
    if (gestureMappings[i].gestureClass == gestureClass) {
      return gestureMappings[i].filename;
    }
  }
  return "";
}

void playWelcomeMessage() {
  String welcomePath = TTS_BASE_PATH + currentLanguage + "/hello.mp3";
  if (SD.exists(welcomePath)) {
    audio.connecttoSD(welcomePath.c_str());
    delay(2000);
  }
}

void streamSensorData() {
  if (!sensorStreamingEnabled) return;
  
  // Read sensor values
  int flex1 = analogRead(FLEX_1);
  int flex2 = analogRead(FLEX_2);
  int flex3 = analogRead(FLEX_3);
  int flex4 = analogRead(FLEX_4);
  int flex5 = analogRead(FLEX_5);
  
  // Create JSON for sensor data
  StaticJsonDocument<200> sensorData;
  JsonArray flex = sensorData.createNestedArray("flex");
  flex.add(flex1);
  flex.add(flex2);
  flex.add(flex3);
  flex.add(flex4);
  flex.add(flex5);
  
  sensorData["timestamp"] = millis();
  
  // Send to Serial (backend can read this)
  String sensorString;
  serializeJson(sensorData, sensorString);
  Serial.println("SENSOR:" + sensorString);
}

void blinkSuccess() {
  for (int i = 0; i < 3; i++) {
    digitalWrite(STATUS_LED, HIGH);
    delay(200);
    digitalWrite(STATUS_LED, LOW);
    delay(200);
  }
  digitalWrite(STATUS_LED, HIGH);
}

void blinkError() {
  for (int i = 0; i < 10; i++) {
    digitalWrite(STATUS_LED, HIGH);
    delay(100);
    digitalWrite(STATUS_LED, LOW);
    delay(100);
  }
}

void loop() {
  // Handle audio processing
  audio.loop();
  
  // Stream sensor data if enabled
  static unsigned long lastSensorRead = 0;
  if (millis() - lastSensorRead > 100) { // 10Hz sampling
    streamSensorData();
    lastSensorRead = millis();
  }
  
  // Handle volume control
  static unsigned long lastVolumeCheck = 0;
  if (millis() - lastVolumeCheck > 1000) {
    int analogValue = analogRead(VOLUME_PIN);
    int newVolume = map(analogValue, 0, 4095, 0, 21);
    
    if (abs(newVolume - currentVolume) > 1) {
      currentVolume = newVolume;
      audio.setVolume(currentVolume);
    }
    lastVolumeCheck = millis();
  }
  
  // Status LED management
  if (audio.isRunning()) {
    // Blink during playback
    static unsigned long lastBlink = 0;
    static bool ledState = false;
    if (millis() - lastBlink > 500) {
      ledState = !ledState;
      digitalWrite(STATUS_LED, ledState ? HIGH : LOW);
      lastBlink = millis();
    }
  } else {
    digitalWrite(STATUS_LED, HIGH); // Solid when ready
  }
  
  delay(10);
}
