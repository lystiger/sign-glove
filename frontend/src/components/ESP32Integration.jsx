import React, { useState } from 'react';
import './ESP32Integration.css';

const ESP32Integration = () => {
  const [activeTab, setActiveTab] = useState('setup');

  const tabs = [
    { id: 'setup', label: 'Setup Guide', icon: '🔧' },
    { id: 'code', label: 'Arduino Code', icon: '💻' },
    { id: 'wiring', label: 'Wiring Diagram', icon: '🔌' },
    { id: 'troubleshooting', label: 'Troubleshooting', icon: '🔍' }
  ];

  const setupSteps = [
    {
      step: 1,
      title: 'Prepare SD Card',
      description: 'Format SD card as FAT32 and create folder structure',
      code: 'mkdir -p /sd/tts/en\nmkdir -p /sd/tts/vn\nmkdir -p /sd/tts/fr'
    },
    {
      step: 2,
      title: 'Generate TTS Files',
      description: 'Use the TTS Manager to generate audio files for each language',
      code: 'POST /esp32/generate-tts-files?language=en'
    },
    {
      step: 3,
      title: 'Copy Files to SD',
      description: 'Copy generated TTS files to corresponding folders on SD card',
      code: 'cp hello.mp3 /sd/tts/en/\ncp xin_chao.mp3 /sd/tts/vn/'
    },
    {
      step: 4,
      title: 'Upload Arduino Code',
      description: 'Upload the ESP32 Arduino sketch to your device',
      code: '// Use Arduino IDE or PlatformIO'
    }
  ];

  const arduinoCode = `#include <SD.h>
#include <Audio.h>
#include <WiFi.h>
#include <WebServer.h>

// Pin definitions
#define SD_CS 5
#define SD_MOSI 23
#define SD_MISO 19
#define SD_SCK 18
#define I2S_BCLK 26
#define I2S_LRC 25
#define I2S_DOUT 22

// Audio instance
Audio audio;

// Web server
WebServer server(80);

// Current language
String currentLanguage = "en";

void setup() {
  Serial.begin(115200);
  
  // Initialize SD card
  if (!SD.begin(SD_CS, SD_MOSI, SD_MISO, SD_SCK)) {
    Serial.println("SD Card initialization failed!");
    return;
  }
  Serial.println("SD Card initialized successfully");
  
  // Initialize audio
  audio.setPinout(I2S_BCLK, I2S_LRC, I2S_DOUT);
  audio.setVolume(21); // 0-21
  
  // Setup WiFi
  WiFi.begin("YOUR_SSID", "YOUR_PASSWORD");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\\nWiFi connected");
  Serial.println("IP address: " + WiFi.localIP().toString());
  
  // Setup web server routes
  setupWebServer();
  server.begin();
}

void loop() {
  server.handleClient();
  audio.loop();
}

void setupWebServer() {
  // Language selection endpoint
  server.on("/language", HTTP_POST, []() {
    if (server.hasArg("language")) {
      currentLanguage = server.arg("language");
      server.send(200, "text/plain", "Language set to " + currentLanguage);
    }
  });
  
  // TTS playback endpoint
  server.on("/play", HTTP_POST, []() {
    if (server.hasArg("gesture")) {
      String gesture = server.arg("gesture");
      playTTS(currentLanguage, gesture);
      server.send(200, "text/plain", "Playing TTS for " + gesture);
    }
  });
}

void playTTS(String language, String gesture) {
  String filepath = "/sd/tts/" + language + "/" + gesture + ".mp3";
  
  if (SD.exists(filepath)) {
    audio.connecttoFS(SD, filepath);
    Serial.println("Playing: " + filepath);
  } else {
    Serial.println("File not found: " + filepath);
  }
}`;

  const wiringDiagram = {
    sdCard: [
      { pin: 'CS', esp32: 'GPIO 5', description: 'Chip Select' },
      { pin: 'MOSI', esp32: 'GPIO 23', description: 'Master Out Slave In' },
      { pin: 'MISO', esp32: 'GPIO 19', description: 'Master In Slave Out' },
      { pin: 'SCK', esp32: 'GPIO 18', description: 'Serial Clock' },
      { pin: 'VCC', esp32: '3.3V', description: 'Power Supply' },
      { pin: 'GND', esp32: 'GND', description: 'Ground' }
    ],
    audio: [
      { pin: 'BCLK', esp32: 'GPIO 26', description: 'Bit Clock' },
      { pin: 'LRC', esp32: 'GPIO 25', description: 'Left Right Clock' },
      { pin: 'DOUT', esp32: 'GPIO 22', description: 'Data Out' }
    ]
  };

  const troubleshooting = [
    {
      issue: 'SD Card not detected',
      solution: 'Check wiring, ensure SD card is properly inserted, verify CS pin connection'
    },
    {
      issue: 'Audio not playing',
      solution: 'Check audio connections, verify file format (MP3/WAV), check volume settings'
    },
    {
      issue: 'TTS files not found',
      solution: 'Verify file paths, check folder structure, ensure files were copied correctly'
    },
    {
      issue: 'WiFi connection failed',
      solution: 'Check SSID/password, ensure WiFi credentials are correct'
    }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'setup':
        return (
          <div className="setup-guide">
            <h3>Setup Steps</h3>
            <div className="steps">
              {setupSteps.map((step) => (
                <div key={step.step} className="step">
                  <div className="step-header">
                    <span className="step-number">{step.step}</span>
                    <h4>{step.title}</h4>
                  </div>
                  <p>{step.description}</p>
                  <pre className="code-block">{step.code}</pre>
                </div>
              ))}
            </div>
          </div>
        );

      case 'code':
        return (
          <div className="arduino-code">
            <h3>ESP32 Arduino Sketch</h3>
            <p>Copy this code to your Arduino IDE and upload to your ESP32:</p>
            <pre className="code-block large">{arduinoCode}</pre>
            <div className="code-actions">
              <button className="copy-btn" onClick={() => navigator.clipboard.writeText(arduinoCode)}>
                📋 Copy Code
              </button>
              <button className="download-btn">
                💾 Download .ino
              </button>
            </div>
          </div>
        );

      case 'wiring':
        return (
          <div className="wiring-diagram">
            <h3>Wiring Diagram</h3>
            
            <div className="wiring-section">
              <h4>SD Card Connections</h4>
              <div className="pin-table">
                <div className="pin-header">
                  <span>SD Card Pin</span>
                  <span>ESP32 GPIO</span>
                  <span>Description</span>
                </div>
                {wiringDiagram.sdCard.map((pin, index) => (
                  <div key={index} className="pin-row">
                    <span className="pin-name">{pin.pin}</span>
                    <span className="pin-gpio">{pin.esp32}</span>
                    <span className="pin-desc">{pin.description}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="wiring-section">
              <h4>Audio Connections</h4>
              <div className="pin-table">
                <div className="pin-header">
                  <span>Audio Pin</span>
                  <span>ESP32 GPIO</span>
                  <span>Description</span>
                </div>
                {wiringDiagram.audio.map((pin, index) => (
                  <div key={index} className="pin-row">
                    <span className="pin-name">{pin.pin}</span>
                    <span className="pin-gpio">{pin.esp32}</span>
                    <span className="pin-desc">{pin.description}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="wiring-note">
              <p><strong>Note:</strong> Ensure all connections are secure and use appropriate jumper wires. 
              The ESP32 operates at 3.3V, so make sure your SD card and audio components are compatible.</p>
            </div>
          </div>
        );

      case 'troubleshooting':
        return (
          <div className="troubleshooting">
            <h3>Common Issues & Solutions</h3>
            <div className="issues">
              {troubleshooting.map((item, index) => (
                <div key={index} className="issue">
                  <h4>❌ {item.issue}</h4>
                  <p><strong>Solution:</strong> {item.solution}</p>
                </div>
              ))}
            </div>
            
            <div className="troubleshooting-tips">
              <h4>💡 Additional Tips</h4>
              <ul>
                <li>Always check Serial Monitor for error messages</li>
                <li>Verify file permissions on SD card</li>
                <li>Test with different audio files</li>
                <li>Check power supply stability</li>
              </ul>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="esp32-integration">
      <div className="integration-header">
        <h2>🔌 ESP32 Integration Guide</h2>
        <p>Complete setup guide for ESP32 + SD Card TTS system</p>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {renderContent()}
      </div>
    </div>
  );
};

export default ESP32Integration; 