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

// Control pins
#define STATUS_LED 2
#define SPEAKER_CTRL_PIN 4
#define VOLUME_PIN 33  // Analog pin for volume control

AsyncWebServer server(80);
Audio audio;

// TTS configuration
const String TTS_BASE_PATH = "/tts/";
String currentLanguage = "en";
bool audioEnabled = true;
int currentVolume = 15; // 0-21 range

// Gesture to filename mapping
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
  
  digitalWrite(STATUS_LED, LOW);
  digitalWrite(SPEAKER_CTRL_PIN, HIGH); // Speaker ON by default
  
  Serial.println("ESP32 Audio Player Starting...");
  
  // Initialize SD card
  if (!initializeSDCard()) {
    Serial.println("[ERROR] SD Card initialization failed!");
    blinkError();
    return;
  }
  
  // Initialize Audio
  audio.setPinout(I2S_BCLK, I2S_LRC, I2S_DOUT);
  audio.setVolume(currentVolume); // 0...21
  
  // Connect to WiFi
  if (!connectToWiFi()) {
    Serial.println("[ERROR] WiFi connection failed!");
    blinkError();
    return;
  }
  
  // Setup web server
  setupWebServerRoutes();
  server.begin();
  
  Serial.println("ESP32 Audio Player Ready!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  digitalWrite(STATUS_LED, HIGH);
  
  // Test audio system
  playWelcomeMessage();
}

bool initializeSDCard() {
  Serial.println("Initializing SD card...");
  
  SPI.begin(SD_SCK_PIN, SD_MISO_PIN, SD_MOSI_PIN, SD_CS_PIN);
  
  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("SD card initialization failed!");
    return false;
  }
  
  uint64_t cardSize = SD.cardSize() / (1024 * 1024);
  Serial.printf("SD Card Size: %lluMB\n", cardSize);
  
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

void setupWebServerRoutes() {
  // Health check
  server.on("/health", HTTP_GET, [](AsyncWebServerRequest *request){
    StaticJsonDocument<300> response;
    response["status"] = "ok";
    response["device"] = "ESP32 Audio Player";
    response["language"] = currentLanguage;
    response["volume"] = currentVolume;
    response["audio_enabled"] = audioEnabled;
    response["free_space"] = SD.totalBytes() - SD.usedBytes();
    
    String responseString;
    serializeJson(response, responseString);
    request->send(200, "application/json", responseString);
  });
  
  // Play gesture audio
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
    
    String responseString;
    serializeJson(response, responseString);
    request->send(success ? 200 : 500, "application/json", responseString);
  });
  
  // Set language
  server.on("/set_language", HTTP_POST, [](AsyncWebServerRequest *request){
    if (!request->hasParam("language", true)) {
      request->send(400, "text/plain", "Missing language parameter");
      return;
    }
    
    String newLanguage = request->getParam("language", true)->value();
    
    // Validate language
    String langPath = TTS_BASE_PATH + newLanguage;
    if (!SD.exists(langPath)) {
      request->send(400, "text/plain", "Language not available");
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
  
  // Volume control
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
    Serial.println("Volume set to: " + String(currentVolume));
    
    StaticJsonDocument<100> response;
    response["status"] = "success";
    response["volume"] = currentVolume;
    
    String responseString;
    serializeJson(response, responseString);
    request->send(200, "application/json", responseString);
  });
  
  // Speaker control
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
  
  // List available files
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
}

bool playGestureAudio(String gestureClass, String language) {
  if (!audioEnabled) {
    Serial.println("Audio disabled, skipping playback");
    return false;
  }
  
  // Find gesture mapping
  String filename = "";
  for (int i = 0; i < NUM_GESTURES; i++) {
    if (gestureMappings[i].gestureClass == gestureClass) {
      filename = gestureMappings[i].filename;
      break;
    }
  }
  
  if (filename == "") {
    Serial.println("Unknown gesture: " + gestureClass);
    return false;
  }
  
  // Build file path
  String filePath = TTS_BASE_PATH + language + "/" + filename;
  
  // Check if file exists
  if (!SD.exists(filePath)) {
    Serial.println("Audio file not found: " + filePath);
    return false;
  }
  
  // Stop current audio
  audio.stopSong();
  
  // Play audio file
  Serial.println("Playing: " + filePath);
  bool success = audio.connecttoSD(filePath.c_str());
  
  if (success) {
    // Blink status LED during playback
    blinkDuringPlayback();
  }
  
  return success;
}

void playWelcomeMessage() {
  Serial.println("Playing welcome message...");
  String welcomePath = TTS_BASE_PATH + currentLanguage + "/hello.mp3";
  
  if (SD.exists(welcomePath)) {
    audio.connecttoSD(welcomePath.c_str());
    delay(2000); // Give time for welcome message
  }
}

void blinkDuringPlayback() {
  // Non-blocking blink during audio playback
  static unsigned long lastBlink = 0;
  static bool ledState = false;
  
  if (millis() - lastBlink > 500) {
    ledState = !ledState;
    digitalWrite(STATUS_LED, ledState ? HIGH : LOW);
    lastBlink = millis();
  }
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
  
  // Handle volume control from analog pin
  static unsigned long lastVolumeCheck = 0;
  if (millis() - lastVolumeCheck > 1000) {
    int analogValue = analogRead(VOLUME_PIN);
    int newVolume = map(analogValue, 0, 4095, 0, 21);
    
    if (abs(newVolume - currentVolume) > 1) {
      currentVolume = newVolume;
      audio.setVolume(currentVolume);
      Serial.println("Volume adjusted to: " + String(currentVolume));
    }
    
    lastVolumeCheck = millis();
  }
  
  // Blink during playback
  if (audio.isRunning()) {
    blinkDuringPlayback();
  } else {
    digitalWrite(STATUS_LED, HIGH); // Solid when not playing
  }
  
  delay(10);
}
