import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { api } from '../api';
import LanguageSelector from '../components/LanguageSelector';
import TTSTest from '../components/TTSTest';
import TTSStatus from '../components/TTSStatus';
import '../pages/styling/TTSManager.css';

const TTSManager = () => {
  const [currentLanguage, setCurrentLanguage] = useState('en');
  const [ttsConfig, setTtsConfig] = useState(null);
  const [sdStructure, setSdStructure] = useState(null);
  const [ttsFiles, setTtsFiles] = useState([]);
  const [generatingFiles, setGeneratingFiles] = useState(false);
  const [loading, setLoading] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'vn', name: 'Vietnamese', flag: '🇻🇳' },
    { code: 'fr', name: 'French', flag: '🇫🇷' }
  ];

  useEffect(() => {
    loadTTSData();
  }, [currentLanguage]);

  const loadTTSData = async () => {
    try {
      setLoading(true);

      // Load TTS configuration
      const configResponse = await api.get('/utils/tts/config');
      setTtsConfig(configResponse.data);

      // Load SD card structure
      const structureResponse = await api.get('/esp32/sd-structure');
      setSdStructure(structureResponse.data.sd_structure);

      // Load TTS files for current language
      const filesResponse = await api.get(`/esp32/tts-files?language=${currentLanguage}`);
      setTtsFiles(filesResponse.data.files);

    } catch (err) {
      toast.error(`Failed to load TTS data: ${err.message || err}`);
      console.error('Error loading TTS data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLanguageChange = (languageCode) => {
    setCurrentLanguage(languageCode);
  };

  const generateTTSFiles = async () => {
    try {
      setGeneratingFiles(true);

      const response = await api.post(`/esp32/generate-tts-files?language=${currentLanguage}`);
      
      if (response.data.status === 'success') {
        toast.success(`Generated ${response.data.total_generated} TTS files for ${currentLanguage.toUpperCase()}`);
        loadTTSData(); // Reload data
        setRefreshTrigger(prev => prev + 1); // Trigger status refresh
      } else {
        toast.error('Failed to generate TTS files');
      }

    } catch (err) {
      toast.error(`Failed to generate TTS files: ${err.message || err}`);
      console.error('Error generating TTS files:', err);
    } finally {
      setGeneratingFiles(false);
    }
  };

  const getLanguageName = (code) => {
    return languages.find(lang => lang.code === code)?.name || code.toUpperCase();
  };

  const getLanguageFlag = (code) => {
    return languages.find(lang => lang.code === code)?.flag || '🌐';
  };

  const handleTestComplete = (gesture, language, result) => {
    console.log(`TTS test completed for ${gesture} in ${language}:`, result);
    // You can add additional logic here if needed
  };

  if (loading) {
    return (
      <div className="tts-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading TTS Manager...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="tts-container">
      <div className="tts-header">
        <h1>TTS Manager</h1>
        <p>Manage Text-to-Speech files for ESP32 + SD Card system</p>
      </div>

      {/* System Status */}
      <TTSStatus refreshTrigger={refreshTrigger} />

      {/* Language Selection */}
      <div className="language-selector">
        <h2>Select Language</h2>
        <LanguageSelector
          currentLanguage={currentLanguage}
          onLanguageChange={handleLanguageChange}
          showFlags={true}
          compact={false}
        />
      </div>

      {/* Current Language Info */}
      <div className="current-language-info">
        <h3>Current Language: {getLanguageFlag(currentLanguage)} {getLanguageName(currentLanguage)}</h3>
        <div className="language-stats">
          <div className="stat">
            <span className="label">Total Gestures:</span>
            <span className="value">{ttsFiles.length}</span>
          </div>
          <div className="stat">
            <span className="label">TTS Enabled:</span>
            <span className="value">{ttsConfig?.filter_idle_gestures ? 'Yes' : 'No'}</span>
          </div>
        </div>
      </div>

      {/* TTS Test Component */}
      <TTSTest 
        gestureLabel="Class 0"
        onTestComplete={handleTestComplete}
      />

      {/* TTS File Management */}
      <div className="tts-files-section">
        <div className="section-header">
          <h2>TTS Files for {getLanguageName(currentLanguage)}</h2>
          <button 
            className="generate-btn"
            onClick={generateTTSFiles}
            disabled={generatingFiles}
          >
            {generatingFiles ? 'Generating...' : 'Generate TTS Files'}
          </button>
        </div>

        <div className="tts-files-grid">
          {ttsFiles.map((file, index) => (
            <div key={index} className="tts-file-card">
              <div className="file-info">
                <h4>{file.text}</h4>
                <p className="gesture-label">{file.gesture_label}</p>
                <p className="file-path">{file.esp32_file_path}</p>
              </div>
              <div className="file-actions">
                <button 
                  className="test-btn"
                  onClick={() => {
                    // Test this specific file
                    console.log('Testing file:', file);
                  }}
                >
                  🔊 Test
                </button>
                <button className="download-btn">
                  📥 Download
                </button>
              </div>
            </div>
          ))}
        </div>

        {ttsFiles.length === 0 && (
          <div className="no-files">
            <p>No TTS files found for {getLanguageName(currentLanguage)}</p>
            <p>Click "Generate TTS Files" to create them</p>
          </div>
        )}
      </div>

      {/* SD Card Structure */}
      {sdStructure && (
        <div className="sd-structure-section">
          <h2>SD Card Structure</h2>
          <div className="structure-tree">
            <div className="folder">
              <span className="folder-icon">📁</span>
              <span className="folder-name">{sdStructure.sd_root}</span>
              <div className="subfolder">
                <span className="folder-icon">📁</span>
                <span className="folder-name">{sdStructure.tts_folder}</span>
                {Object.entries(sdStructure.languages).map(([lang, langInfo]) => (
                  <div key={lang} className="subfolder">
                    <span className="folder-icon">📁</span>
                    <span className="folder-name">{langInfo.path}</span>
                    <div className="files">
                      {langInfo.files.map((file, index) => (
                        <div key={index} className="file">
                          <span className="file-icon">🎵</span>
                          <span className="file-name">{file}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TTSManager; 