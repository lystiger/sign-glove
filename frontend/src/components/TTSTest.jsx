import React, { useState } from 'react';
import { api } from '../api';
import LanguageSelector from './LanguageSelector';
import './TTSTest.css';

const TTSTest = ({ gestureLabel, onTestComplete }) => {
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [testResult, setTestResult] = useState(null);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState(null);

  const gestures = [
    { label: 'Class 0', name: 'Hello' },
    { label: 'Class 1', name: 'Yes' },
    { label: 'Class 2', name: 'No' },
    { label: 'Class 3', name: 'Thank you' },
    { label: 'Class 4', name: 'Please' },
    { label: 'Class 5', name: 'Sorry' },
    { label: 'Class 6', name: 'Goodbye' },
    { label: 'Class 7', name: 'Help' },
    { label: 'Class 8', name: 'Water' },
    { label: 'Class 9', name: 'Food' },
    { label: 'Class 10', name: 'Emergency' }
  ];

  const handleLanguageChange = (languageCode) => {
    setSelectedLanguage(languageCode);
    setTestResult(null);
    setError(null);
  };

  const testTTS = async (gesture) => {
    try {
      setTesting(true);
      setError(null);
      setTestResult(null);

      const response = await api.post('/utils/tts/test-gesture', {
        gesture_label: gesture,
        language: selectedLanguage
      });

      setTestResult(response.data.result);
      
      if (onTestComplete) {
        onTestComplete(gesture, selectedLanguage, response.data.result);
      }
    } catch (err) {
      setError('Failed to test TTS');
      console.error('TTS test error:', err);
    } finally {
      setTesting(false);
    }
  };

  const testAllGestures = async () => {
    try {
      setTesting(true);
      setError(null);
      setTestResult(null);

      const response = await api.post('/utils/tts/test-multilingual', {
        gesture_label: gestureLabel || 'Class 0'
      });

      setTestResult(response.data.results);
      
      if (onTestComplete) {
        onTestComplete(gestureLabel || 'Class 0', 'all', response.data.results);
      }
    } catch (err) {
      setError('Failed to test all languages');
      console.error('Multilingual TTS test error:', err);
    } finally {
      setTesting(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return '✅';
      case 'skipped':
        return '⏭️';
      case 'error':
        return '❌';
      default:
        return '❓';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'skipped':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'info';
    }
  };

  return (
    <div className="tts-test">
      <div className="test-header">
        <h3>🔊 TTS Test</h3>
        <p>Test Text-to-Speech for different gestures and languages</p>
      </div>

      {/* Language Selection */}
      <div className="language-section">
        <label>Select Language:</label>
        <LanguageSelector
          currentLanguage={selectedLanguage}
          onLanguageChange={handleLanguageChange}
          showFlags={true}
          compact={false}
        />
      </div>

      {/* Gesture Selection */}
      <div className="gesture-section">
        <label>Select Gesture:</label>
        <div className="gesture-grid">
          {gestures.map(gesture => (
            <button
              key={gesture.label}
              className={`gesture-btn ${gestureLabel === gesture.label ? 'active' : ''}`}
              onClick={() => testTTS(gesture.label)}
              disabled={testing}
            >
              <span className="gesture-label">{gesture.label}</span>
              <span className="gesture-name">{gesture.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Test All Languages Button */}
      <div className="test-all-section">
        <button
          className="test-all-btn"
          onClick={testAllGestures}
          disabled={testing}
        >
          {testing ? 'Testing...' : 'Test All Languages'}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <span>❌ {error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Test Results */}
      {testResult && (
        <div className="test-results">
          <h4>Test Results:</h4>
          
          {Array.isArray(testResult) ? (
            // Multilingual results
            <div className="multilingual-results">
              {Object.entries(testResult).map(([language, result]) => (
                <div key={language} className={`result-card ${getStatusColor(result.status)}`}>
                  <div className="result-header">
                    <span className="language-flag">
                      {language === 'en' ? '🇺🇸' : language === 'vn' ? '🇻🇳' : '🇫🇷'}
                    </span>
                    <span className="language-name">{language.toUpperCase()}</span>
                    <span className="status-icon">{getStatusIcon(result.status)}</span>
                  </div>
                  <div className="result-details">
                    <p><strong>Status:</strong> {result.status}</p>
                    {result.reason && <p><strong>Reason:</strong> {result.reason}</p>}
                    {result.message && <p><strong>Message:</strong> {result.message}</p>}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            // Single result
            <div className={`result-card ${getStatusColor(testResult.status)}`}>
              <div className="result-header">
                <span className="status-icon">{getStatusIcon(testResult.status)}</span>
                <span className="result-status">{testResult.status}</span>
              </div>
              <div className="result-details">
                {testResult.reason && <p><strong>Reason:</strong> {testResult.reason}</p>}
                {testResult.message && <p><strong>Message:</strong> {testResult.message}</p>}
                {testResult.provider && <p><strong>Provider:</strong> {testResult.provider}</p>}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Loading State */}
      {testing && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Testing TTS...</p>
        </div>
      )}
    </div>
  );
};

export default TTSTest; 