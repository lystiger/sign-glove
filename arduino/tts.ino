#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <SPIFFS.h>
#include "AudioFileSourceSPIFFS.h"
#include "AudioGeneratorMP3.h"
#include "AudioOutputI2S.h"
#include <time.h>

// WiFi credentials
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

#define STATUS_LED 2
#define SPEAKER_CTRL_PIN 4

AsyncWebServer server(80);

AudioGeneratorMP3 *mp3;
AudioFileSourceSPIFFS *file;
AudioOutputI2S *out;

// Helper: log error to SPIFFS file with timestamp
void logError(const String& msg) {
  String logMsg = String("[") + millis() + "] " + msg + "\n";
  File logFile = SPIFFS.open("/error.log", "a");
  if (logFile) {
    logFile.print(logMsg);
    logFile.close();
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(STATUS_LED, OUTPUT);
  digitalWrite(STATUS_LED, LOW); // Idle
  pinMode(SPEAKER_CTRL_PIN, OUTPUT);
  digitalWrite(SPEAKER_CTRL_PIN, HIGH); // Speaker ON by default

  // Connect to WiFi
  WiFi.begin(ssid, password);
  unsigned long wifiStart = millis();
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    if (millis() - wifiStart > 20000) { // 20s timeout
      Serial.println("[ERROR] WiFi connection failed");
      logError("WiFi connection failed");
      blinkError();
      return;
    }
  }
  Serial.println("WiFi connected");
  digitalWrite(STATUS_LED, HIGH); // Connected

  // Initialize SPIFFS
  if (!SPIFFS.begin(true)) {
    Serial.println("[ERROR] SPIFFS Mount Failed");
    logError("SPIFFS Mount Failed");
    blinkError();
    return;
  }

  // Define /play_audio endpoint
  server.on("/play_audio", HTTP_POST, [](AsyncWebServerRequest *request){},
    NULL,
    [](AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t index, size_t total) {
      File f = SPIFFS.open("/audio.mp3", index == 0 ? "w" : "a");
      if (!f) {
        Serial.println("[ERROR] Failed to open file for writing");
        logError("Failed to open file for writing");
        request->send(500, "text/plain", "Failed to save audio");
        return;
      }
      size_t written = f.write(data, len);
      f.close();
      if (written != len) {
        Serial.printf("[ERROR] Only wrote %u/%u bytes to file\n", (unsigned)written, (unsigned)len);
        logError(String("Only wrote ") + written + "/" + len + " bytes to file");
        blinkError();
        request->send(500, "text/plain", "Failed to write all audio data");
        return;
      }
      if (index + len == total) {
        Serial.println("[INFO] Audio file received, starting playback...");
        request->send(200, "text/plain", "Audio received, playing...");
        if (!playAudio("/audio.mp3")) {
          blinkError();
        }
      }
    }
  );

  // Speaker ON endpoint
  server.on("/speaker/on", HTTP_POST, [](AsyncWebServerRequest *request){
    digitalWrite(SPEAKER_CTRL_PIN, HIGH);
    Serial.println("[INFO] Speaker turned ON");
    request->send(200, "text/plain", "Speaker ON");
  });
  // Speaker OFF endpoint
  server.on("/speaker/off", HTTP_POST, [](AsyncWebServerRequest *request){
    digitalWrite(SPEAKER_CTRL_PIN, LOW);
    Serial.println("[INFO] Speaker turned OFF");
    request->send(200, "text/plain", "Speaker OFF");
  });

  server.begin();
}

// Blink status LED for error
void blinkError() {
  for (int i = 0; i < 10; i++) {
    digitalWrite(STATUS_LED, HIGH);
    delay(100);
    digitalWrite(STATUS_LED, LOW);
    delay(100);
  }
}

// Returns true if playback succeeded, false if error
bool playAudio(const char* path) {
  if (!SPIFFS.exists(path)) {
    Serial.println("[ERROR] Audio file does not exist");
    logError("Audio file does not exist");
    return false;
  }
  if (mp3) {
    mp3->stop();
    delete mp3;
    mp3 = nullptr;
  }
  if (file) {
    delete file;
    file = nullptr;
  }
  if (out) {
    delete out;
    out = nullptr;
  }

  file = new AudioFileSourceSPIFFS(path);
  out = new AudioOutputI2S();
  mp3 = new AudioGeneratorMP3();
  if (!mp3->begin(file, out)) {
    Serial.println("[ERROR] Failed to start MP3 playback");
    logError("Failed to start MP3 playback");
    return false;
  }
  Serial.println("[INFO] Playback started");
  // Play in loop until done
  while (mp3->isRunning()) {
    if (!mp3->loop()) break;
    delay(1);
  }
  mp3->stop();
  Serial.println("[INFO] Playback finished");
  return true;
}

void loop() {
  // Nothing needed here for AsyncWebServer
}