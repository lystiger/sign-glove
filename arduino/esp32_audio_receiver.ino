#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <SD.h>
#include <SPI.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

// SD Card pins for ESP32
#define SD_CS_PIN 5
#define SD_MOSI_PIN 23
#define SD_MISO_PIN 19
#define SD_SCK_PIN 18

// Status LED
#define STATUS_LED 2
#define ERROR_LED 4

AsyncWebServer server(80);

// TTS folder structure on SD card
const String TTS_BASE_PATH = "/tts/";
const String LANGUAGES[] = {"en", "vn", "fr"};
const int NUM_LANGUAGES = 3;

void setup() {
  Serial.begin(115200);
  
  // Initialize pins
  pinMode(STATUS_LED, OUTPUT);
  pinMode(ERROR_LED, OUTPUT);
  digitalWrite(STATUS_LED, LOW);
  digitalWrite(ERROR_LED, LOW);
  
  Serial.println("ESP32 Audio Receiver Starting...");
  
  // Initialize SD card
  if (!initializeSDCard()) {
    Serial.println("[ERROR] SD Card initialization failed!");
    blinkError();
    return;
  }
  
  // Connect to WiFi
  if (!connectToWiFi()) {
    Serial.println("[ERROR] WiFi connection failed!");
    blinkError();
    return;
  }
  
  // Create TTS folder structure
  createTTSFolderStructure();
  
  // Setup web server endpoints
  setupWebServerRoutes();
  
  server.begin();
  Serial.println("ESP32 Audio Receiver Ready!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  digitalWrite(STATUS_LED, HIGH);
}

bool initializeSDCard() {
  Serial.println("Initializing SD card...");
  
  // Initialize SPI with custom pins
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
  
  Serial.print("SD Card Type: ");
  if (cardType == CARD_MMC) {
    Serial.println("MMC");
  } else if (cardType == CARD_SD) {
    Serial.println("SDSC");
  } else if (cardType == CARD_SDHC) {
    Serial.println("SDHC");
  } else {
    Serial.println("UNKNOWN");
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
    
    if (millis() - startTime > 20000) { // 20 second timeout
      return false;
    }
  }
  
  Serial.println("\nWiFi connected!");
  return true;
}

void createTTSFolderStructure() {
  Serial.println("Creating TTS folder structure...");
  
  // Create base TTS folder
  if (!SD.exists(TTS_BASE_PATH)) {
    SD.mkdir(TTS_BASE_PATH);
    Serial.println("Created /tts/ folder");
  }
  
  // Create language folders
  for (int i = 0; i < NUM_LANGUAGES; i++) {
    String langPath = TTS_BASE_PATH + LANGUAGES[i];
    if (!SD.exists(langPath)) {
      SD.mkdir(langPath);
      Serial.println("Created " + langPath + " folder");
    }
  }
}

void setupWebServerRoutes() {
  // Health check endpoint
  server.on("/health", HTTP_GET, [](AsyncWebServerRequest *request){
    StaticJsonDocument<200> response;
    response["status"] = "ok";
    response["device"] = "ESP32 Audio Receiver";
    response["free_space"] = SD.totalBytes() - SD.usedBytes();
    response["total_space"] = SD.totalBytes();
    
    String responseString;
    serializeJson(response, responseString);
    request->send(200, "application/json", responseString);
  });
  
  // List files endpoint
  server.on("/files", HTTP_GET, [](AsyncWebServerRequest *request){
    String language = "en";
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
        if (!file.isDirectory()) {
          JsonObject fileObj = files.createNestedObject();
          fileObj["name"] = String(file.name());
          fileObj["size"] = file.size();
        }
        file = dir.openNextFile();
      }
    }
    dir.close();
    
    String responseString;
    serializeJson(response, responseString);
    request->send(200, "application/json", responseString);
  });
  
  // Upload audio file endpoint
  server.on("/upload_audio", HTTP_POST, 
    [](AsyncWebServerRequest *request) {
      // This will be called when upload is complete
    },
    [](AsyncWebServerRequest *request, String filename, size_t index, uint8_t *data, size_t len, bool final) {
      handleFileUpload(request, filename, index, data, len, final);
    }
  );
  
  // Delete file endpoint
  server.on("/delete_file", HTTP_DELETE, [](AsyncWebServerRequest *request){
    if (!request->hasParam("file")) {
      request->send(400, "text/plain", "Missing file parameter");
      return;
    }
    
    String filePath = request->getParam("file")->value();
    if (!filePath.startsWith("/tts/")) {
      request->send(400, "text/plain", "Invalid file path");
      return;
    }
    
    if (SD.remove(filePath)) {
      request->send(200, "text/plain", "File deleted successfully");
      Serial.println("Deleted: " + filePath);
    } else {
      request->send(500, "text/plain", "Failed to delete file");
    }
  });
}

void handleFileUpload(AsyncWebServerRequest *request, String filename, size_t index, uint8_t *data, size_t len, bool final) {
  static File uploadFile;
  static String currentFilePath;
  
  // Get parameters
  String language = "en";
  String gestureLabel = "unknown";
  
  if (request->hasParam("language")) {
    language = request->getParam("language")->value();
  }
  if (request->hasParam("gesture")) {
    gestureLabel = request->getParam("gesture")->value();
  }
  
  // Start of upload
  if (index == 0) {
    // Create file path: /tts/en/hello.mp3
    currentFilePath = TTS_BASE_PATH + language + "/" + filename;
    
    Serial.println("Starting upload: " + currentFilePath);
    
    // Open file for writing
    uploadFile = SD.open(currentFilePath, FILE_WRITE);
    if (!uploadFile) {
      Serial.println("Failed to open file for writing");
      request->send(500, "text/plain", "Failed to create file");
      return;
    }
  }
  
  // Write data chunk
  if (uploadFile && len > 0) {
    size_t written = uploadFile.write(data, len);
    if (written != len) {
      Serial.printf("Write error: %d/%d bytes written\n", written, len);
    }
  }
  
  // End of upload
  if (final) {
    if (uploadFile) {
      uploadFile.close();
      Serial.println("Upload completed: " + currentFilePath);
      Serial.printf("File size: %d bytes\n", SD.open(currentFilePath).size());
      
      StaticJsonDocument<200> response;
      response["status"] = "success";
      response["file_path"] = currentFilePath;
      response["language"] = language;
      response["gesture"] = gestureLabel;
      
      String responseString;
      serializeJson(response, responseString);
      request->send(200, "application/json", responseString);
      
      // Blink success
      blinkSuccess();
    } else {
      request->send(500, "text/plain", "Upload failed");
      blinkError();
    }
  }
}

void blinkSuccess() {
  for (int i = 0; i < 3; i++) {
    digitalWrite(STATUS_LED, HIGH);
    delay(200);
    digitalWrite(STATUS_LED, LOW);
    delay(200);
  }
  digitalWrite(STATUS_LED, HIGH); // Keep on
}

void blinkError() {
  for (int i = 0; i < 10; i++) {
    digitalWrite(ERROR_LED, HIGH);
    delay(100);
    digitalWrite(ERROR_LED, LOW);
    delay(100);
  }
}

void loop() {
  // Handle any background tasks
  delay(100);
  
  // Optional: Print status every 30 seconds
  static unsigned long lastStatus = 0;
  if (millis() - lastStatus > 30000) {
    lastStatus = millis();
    Serial.printf("Status: WiFi=%s, Free Space=%llu bytes\n", 
                  WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected",
                  SD.totalBytes() - SD.usedBytes());
  }
}
