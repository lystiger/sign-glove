import React, { useState, useEffect, useRef } from 'react';
import './VoiceStreaming.css';
import GestureSpeaker from '../utils/tts';

const VoiceStreaming = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [error, setError] = useState(null);
  const [recognitionResults, setRecognitionResults] = useState([]);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isTTSReady, setIsTTSReady] = useState(false);
  
  const wsRef = useRef(null);
  const streamRef = useRef(null);
  const speakerRef = useRef(null);

  // Initialize TTS when component mounts
  useEffect(() => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      speakerRef.current = new GestureSpeaker();
      // Check if voices are already loaded
      if (speakerRef.current.isReady) {
        setIsTTSReady(true);
      } else {
        // Wait for voices to be loaded
        const checkVoices = setInterval(() => {
          if (speakerRef.current.isReady) {
            setIsTTSReady(true);
            clearInterval(checkVoices);
          }
        }, 100);
        
        return () => clearInterval(checkVoices);
      }
    } else {
      setError('Text-to-speech is not supported in this browser');
    }
    
    // Cleanup
    return () => {
      if (speakerRef.current) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  // Check voice system status
  const checkVoiceStatus = async () => {
    try {
      const response = await fetch('/api/voice/status');
      const data = await response.json();
      console.log('Voice status:', data);
    } catch (error) {
      console.error('Failed to check voice status:', error);
      setError('Failed to check voice system status');
    }
  };

  // Connect to WebSocket
  const connectWebSocket = () => {
    try {
      const wsUrl = `ws://${window.location.hostname}:8000/voice/voice`;
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setConnectionStatus('connected');
      };
      
      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('Received message:', data);
          
          if (data.type === 'recognition_result') {
            const newResult = {
              text: data.text,
              confidence: data.confidence,
              timestamp: new Date().toLocaleTimeString()
            };
            
            setRecognitionResults(prev => [
              ...prev.slice(-9), // Keep last 10 results
              newResult
            ]);
            
            // Speak the recognized text
            if (isTTSReady && data.text) {
              speakerRef.current.speak(data.text);
            }
          }
        } catch (error) {
          console.error('Error processing message:', error);
        }
      };
      
      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        setConnectionStatus('disconnected');
        setIsRecording(false);
      };
      
      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection error');
        setConnectionStatus('error');
      };
      
    } catch (error) {
      console.error('Error setting up WebSocket:', error);
      setError('Failed to connect to voice server');
    }
  };

  // Toggle recording
  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  // Start recording
  const startRecording = async () => {
    try {
      // Connect WebSocket if not already connected
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        connectWebSocket();
      }
      
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        } 
      });
      
      streamRef.current = stream;
      setIsRecording(true);
      setConnectionStatus('recording');
      
      // TODO: Add audio processing here if needed
      
    } catch (error) {
      console.error('Error starting recording:', error);
      setError('Failed to access microphone: ' + error.message);
      setIsRecording(false);
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    setIsRecording(false);
    setConnectionStatus('connected');
  };

  // Test TTS with a sample text
  const testTTS = (text) => {
    if (speakerRef.current) {
      setIsSpeaking(true);
      speakerRef.current.speak(text);
      // Reset speaking state after a delay
      setTimeout(() => setIsSpeaking(false), 1000);
    }
  };

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (speakerRef.current) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  return (
    <div className="voice-streaming-container">
      <h2>Voice Streaming</h2>
      
      <div className="status">
        Status: {connectionStatus}
        {!isTTSReady && <div className="warning">Loading TTS voices...</div>}
        {error && <div className="error">{error}</div>}
      </div>
      
      <div className="controls">
        <button 
          onClick={toggleRecording}
          className={`control-btn ${isRecording ? 'recording' : ''}`}
          disabled={!isConnected && connectionStatus !== 'disconnected'}
        >
          {isRecording ? '⏹️ Stop Recording' : '🎤 Start Recording'}
        </button>
        
        <div className="tts-controls">
          <h4>Test TTS:</h4>
          <div className="tts-buttons">
            {['A', 'B', 'C', 'D', 'Hello', 'Test'].map((char) => (
              <button 
                key={char}
                onClick={() => testTTS(char)}
                disabled={!isTTSReady || isSpeaking}
                className="tts-btn"
              >
                Say "{char}"
              </button>
            ))}
          </div>
        </div>
      </div>
      
      <div className="recognition-results">
        <h3>Recognition Results:</h3>
        <ul>
          {recognitionResults.length > 0 ? (
            recognitionResults.map((result, index) => (
              <li key={index} className="result-item">
                <span className="result-text">{result.text}</span>
                <span className="result-meta">
                  {Math.round(result.confidence * 100)}% - {result.timestamp}
                </span>
              </li>
            ))
          ) : (
            <li className="no-results">No recognition results yet</li>
          )}
        </ul>
      </div>
      
      <style jsx>{`
        .voice-streaming-container {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
          font-family: Arial, sans-serif;
        }
        
        .status {
          margin: 15px 0;
          padding: 10px;
          border-radius: 4px;
          background-color: #f5f5f5;
        }
        
        .error {
          color: #d32f2f;
          margin-top: 5px;
          padding: 5px;
          background-color: #ffebee;
          border-radius: 4px;
        }
        
        .warning {
          color: #ff9800;
          margin-top: 5px;
        }
        
        .controls {
          margin: 20px 0;
        }
        
        .control-btn {
          padding: 10px 20px;
          font-size: 16px;
          border: none;
          border-radius: 4px;
          background-color: #4caf50;
          color: white;
          cursor: pointer;
          margin-right: 10px;
          transition: background-color 0.3s;
        }
        
        .control-btn:disabled {
          background-color: #cccccc;
          cursor: not-allowed;
        }
        
        .control-btn.recording {
          background-color: #f44336;
        }
        
        .tts-controls {
          margin: 20px 0;
        }
        
        .tts-buttons {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          margin-top: 10px;
        }
        
        .tts-btn {
          padding: 8px 12px;
          border: 1px solid #2196f3;
          border-radius: 4px;
          background-color: #e3f2fd;
          color: #1976d2;
          cursor: pointer;
          transition: all 0.2s;
        }
        
        .tts-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        
        .tts-btn:hover:not(:disabled) {
          background-color: #bbdefb;
        }
        
        .recognition-results {
          margin-top: 20px;
        }
        
        .result-item {
          padding: 10px;
          margin: 5px 0;
          background-color: #f9f9f9;
          border-left: 4px solid #2196f3;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .result-text {
          font-weight: bold;
        }
        
        .result-meta {
          color: #666;
          font-size: 0.9em;
        }
        
        .no-results {
          color: #888;
          font-style: italic;
          padding: 10px;
        }
      `}</style>
    </div>
  );
};

export default VoiceStreaming;
