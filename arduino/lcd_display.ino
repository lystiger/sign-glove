#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <SPIFFS.h>

// WiFi credentials
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

#define STATUS_LED 2

AsyncWebServer server(80);
LiquidCrystal_I2C lcd(0x27, 16, 2); // LCD address and size

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

  // Mount SPIFFS for error logging
  if (!SPIFFS.begin(true)) {
    Serial.println("[ERROR] SPIFFS Mount Failed");
    logError("SPIFFS Mount Failed");
    blinkError();
    return;
  }

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

  // Initialize LCD
  if (!lcd.init()) {
    Serial.println("[ERROR] LCD init failed");
    logError("LCD init failed");
    blinkError();
    return;
  }
  lcd.backlight();

  // LCD display endpoint
  server.on("/display_text", HTTP_POST, [](AsyncWebServerRequest *request){},
    NULL,
    [](AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t index, size_t total) {
      static String text = "";
      if (index == 0) text = "";
      for (size_t i = 0; i < len; i++) text += (char)data[i];
      if (index + len == total) {
        if (!displayText(text)) {
          blinkError();
          request->send(500, "text/plain", "Failed to display text");
          return;
        }
        Serial.printf("[INFO] Displayed text: %s\n", text.c_str());
        request->send(200, "text/plain", "Text displayed");
      }
    }
  );

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

// Returns true if display succeeded, false if error
bool displayText(const String& text) {
  lcd.clear();
  lcd.setCursor(0, 0);
  if (lcd.print(text.substring(0, 16)) != text.substring(0, 16).length()) {
    Serial.println("[ERROR] Failed to print first line");
    logError("Failed to print first line");
    return false;
  }
  if (text.length() > 16) {
    lcd.setCursor(0, 1);
    if (lcd.print(text.substring(16, 32)) != text.substring(16, 32).length()) {
      Serial.println("[ERROR] Failed to print second line");
      logError("Failed to print second line");
      return false;
    }
  }
  return true;
}

void loop() {
  // Nothing needed here for AsyncWebServer
} 