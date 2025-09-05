import React, { useState, useRef, useEffect, useCallback } from 'react';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { MdLink, MdVolumeUp } from 'react-icons/md';

const LivePredict = () => {
  // State variables
  const [prediction, setPrediction] = useState(null);
  const [connected, setConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  const [ttsEnabled, setTtsEnabled] = useState(false);
  const [isTtsSupported, setIsTtsSupported] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const predictionInterval = useRef(null);

  // Refs for WebSocket and reconnect
  const wsRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectTimeout = useRef(null);
  const utteranceRef = useRef(null);

  // Kiểm tra hỗ trợ TTS khi component mount
  useEffect(() => {
    const ttsSupported = 'speechSynthesis' in window;
    setIsTtsSupported(ttsSupported);
    
    if (ttsSupported) {
      console.log('Trình duyệt hỗ trợ speechSynthesis');
      
      // Preload voices
      window.speechSynthesis.getVoices();
      
      // Sự kiện khi voices được load
      window.speechSynthesis.onvoiceschanged = () => {
        console.log('Voices loaded:', window.speechSynthesis.getVoices().length);
      };
    } else {
      console.error('Trình duyệt không hỗ trợ speechSynthesis');
      toast.error('Trình duyệt của bạn không hỗ trợ chức năng đọc văn bản');
    }
  }, []);

  // Hàm phát âm thanh đã được cải tiến
  const speakText = useCallback((text) => {
    if (!isTtsSupported || !text || isSpeaking) return false;
    
    try {
      // Dừng bất kỳ âm thanh nào đang phát
      if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        setIsSpeaking(false);
      }
      
      // Tạo utterance mới
      utteranceRef.current = new SpeechSynthesisUtterance(text);
      utteranceRef.current.lang = 'en-US';
      utteranceRef.current.rate = 0.9;
      utteranceRef.current.volume = 1.0;
      utteranceRef.current.pitch = 1.0;
      
      // Xử lý sự kiện
      utteranceRef.current.onstart = () => {
        console.log('Start playing voice:', text);
        setIsSpeaking(true);
      };
      
      utteranceRef.current.onend = () => {
        console.log('End playing voice');
        setIsSpeaking(false);
      };
      
      utteranceRef.current.onerror = (event) => {
        console.error('Error:', event.error);
        setIsSpeaking(false);
        toast.error('Can Play Voice Audio: ' + event.error);
      };
      
      // Phát âm thanh
      window.speechSynthesis.speak(utteranceRef.current);
      return true;
    } catch (error) {
      console.error('Error in speakText:', error);
      setIsSpeaking(false);
      return false;
    }
  }, [isTtsSupported, isSpeaking]);

  // Kích hoạt TTS với tương tác người dùng
  const enableTTS = useCallback(() => {
    if (!isTtsSupported) {
      toast.error('Trình duyệt không hỗ trợ chức năng đọc văn bản');
      return;
    }
    
    // Kiểm tra xem TTS đã được kích hoạt chưa
    if (ttsEnabled) {
      setTtsEnabled(false);
      // Dừng âm thanh nếu đang phát
      if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        setIsSpeaking(false);
      }
      toast.info('Text to speech disabled');
      return;
    }
    
    // Kích hoạt TTS bằng cách phát một đoạn text ngắn
    const success = speakText('Text to speech is now enabled');
    
    if (success) {
      setTtsEnabled(true);
      toast.success('Đã bật chức năng đọc văn bản');
    } else {
      toast.error('Không thể kích hoạt chức năng đọc văn bản');
    }
  }, [isTtsSupported, ttsEnabled, speakText]);

  // Phát prediction hiện tại
  const speakCurrentPrediction = useCallback(() => {
    if (!prediction || isSpeaking) return;
    
    let predictionText;
    if (typeof prediction === 'string') {
      predictionText = prediction;
    } else if (prediction.prediction) {
      predictionText = prediction.prediction;
    } else if (prediction.class) {
      predictionText = prediction.class;
    } else {
      predictionText = JSON.stringify(prediction);
    }
    
    if (predictionText) {
      speakText(predictionText);
    }
  }, [prediction, isSpeaking, speakText]);

  // Xử lý dự đoán từ WebSocket
  useEffect(() => {
    if (!wsRef.current) return;

    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.error) {
          console.error('WebSocket error:', data.error);
          toast.error(`Prediction error: ${data.error}`);
          return;
        }
        
        if (data.prediction) {
          setPrediction(data.prediction);
          
          // Tự động phát âm thanh nếu TTS đã được kích hoạt
          if (ttsEnabled) {
            // Sử dụng setTimeout để đảm bảo giao diện được cập nhật trước
            setTimeout(() => {
              speakText(data.prediction);
            }, 100);
          }
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
  }, [ttsEnabled, speakText]);

  // Kết nối WebSocket (giữ nguyên từ code gốc)
  const connectWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (isConnecting) return;

    setIsConnecting(true);
    setConnectionError(null);

    const wsUrl = window.env?.REACT_APP_WS_URL || 'ws://localhost:8000/ws/predict';
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
      setIsConnecting(false);
      reconnectAttempts.current = 0;
      toast.success('Connected to gesture recognition service');
    
      // Send initial hand data with zeros for one hand (right hand in this case)
      const initialData = {
        right: {
          values: Array(11).fill(0),
          timestamp: Date.now()
        },
        language: 'en'
      };
      ws.send(JSON.stringify(initialData));
    };

    ws.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason);
      setConnected(false);
      setIsConnecting(false);

      // Attempt reconnection unless closed normally
      if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
        console.log(`Reconnecting in ${delay}ms...`);

        reconnectTimeout.current = setTimeout(() => {
          reconnectAttempts.current += 1;
          connectWebSocket();
        }, delay);
      } else if (reconnectAttempts.current >= maxReconnectAttempts) {
        setConnectionError('Failed to connect after multiple attempts. Please try again later.');
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionError('Connection error. Please check your network and try again.');
      setIsConnecting(false);
    };
  }, [isConnecting]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (predictionInterval.current) {
        clearInterval(predictionInterval.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      // Dừng phát âm thanh khi component unmount
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  // Reset prediction function
  const resetPrediction = useCallback(() => {
    setPrediction(null);
  }, []);

  return (
    <div role="main" aria-label="Live Prediction Page" style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <div className="live-predict-container" style={{ maxWidth: '800px', margin: '0 auto' }}>
        <div className="card fade-in" style={{
          background: 'white',
          borderRadius: '8px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
          padding: '20px',
          marginBottom: '20px'
        }}>
          <div className="header-row" style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px',
            flexWrap: 'wrap',
            gap: '10px'
          }}>
            <h2 id="gesture-prediction-title" tabIndex={0} style={{ margin: 0, color: '#333' }}>Gesture Recognition</h2>
            <div style={{ 
              display: 'flex', 
              gap: '10px', 
              alignItems: 'center',
              flexWrap: 'wrap'
            }}>
              <button
                onClick={speakCurrentPrediction}
                className="speak-button"
                aria-label="Speak current prediction"
                title="Click to hear the prediction"
                disabled={!prediction || isSpeaking}
                style={{
                  background: prediction && !isSpeaking ? '#4CAF50' : '#9e9e9e',
                  border: 'none',
                  borderRadius: '50%',
                  width: '40px',
                  height: '40px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: prediction && !isSpeaking ? 'pointer' : 'not-allowed',
                  transition: 'all 0.2s',
                  color: 'white'
                }}
              >
                <MdVolumeUp size={20} />
                {isSpeaking && (
                  <span style={{
                    position: 'absolute',
                    top: '-5px',
                    right: '-5px',
                    width: '12px',
                    height: '12px',
                    borderRadius: '50%',
                    background: '#f44336',
                    animation: 'pulse 1s infinite'
                  }}></span>
                )}
              </button>
              
              <button
                onClick={() => {
                  speakText('This is a TTS test. If you can hear this, text to speech is working properly.');
                }}
                className="test-tts-button"
                aria-label="Test TTS"
                title="Click to test text-to-speech"
                disabled={!isTtsSupported || isSpeaking}
                style={{
                  background: isTtsSupported && !isSpeaking ? '#2196F3' : '#9e9e9e',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  padding: '8px 12px',
                  cursor: isTtsSupported && !isSpeaking ? 'pointer' : 'not-allowed',
                  fontSize: '12px',
                  fontWeight: 'bold'
                }}
              >
                Test TTS
              </button>
              
              <button
                onClick={enableTTS}
                className="tts-enable-button"
                aria-label="Enable/Disable TTS"
                title="Click to enable or disable text-to-speech"
                disabled={!isTtsSupported}
                style={{
                  background: ttsEnabled ? '#4CAF50' : (isTtsSupported ? '#9e9e9e' : '#cccccc'),
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  padding: '8px 16px',
                  cursor: isTtsSupported ? 'pointer' : 'not-allowed',
                  fontSize: '14px',
                  fontWeight: 'bold'
                }}
              >
                {ttsEnabled ? 'TTS Enabled' : 'TTS Disabled'}
              </button>
              
              <button
                onClick={resetPrediction}
                className="reset-button"
                aria-label="Reset prediction"
                title="Click to reset and recognize a new gesture"
                disabled={!prediction}
                style={{
                  background: prediction ? '#f44336' : '#e0e0e0',
                  color: prediction ? 'white' : '#9e9e9e',
                  border: 'none',
                  borderRadius: '4px',
                  padding: '8px 16px',
                  cursor: prediction ? 'pointer' : 'not-allowed',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontWeight: 'bold',
                  transition: 'all 0.2s',
                  fontSize: '14px',
                  minWidth: '80px',
                  justifyContent: 'center'
                }}
              >
                <span>Reset</span>
              </button>
            </div>
          </div>
          
          {/* Hiển thị trạng thái hỗ trợ TTS */}
          {!isTtsSupported && (
            <div style={{
              padding: '10px',
              backgroundColor: '#ffebee',
              borderRadius: '4px',
              marginBottom: '15px',
              borderLeft: '4px solid #f44336',
              fontSize: '14px'
            }}>
              <strong>Trình duyệt không hỗ trợ:</strong> Chức năng đọc văn bản không khả dụng trên trình duyệt này.
              Vui lòng sử dụng Chrome, Edge hoặc Safari.
            </div>
          )}
          
          <div className="connection-controls" style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '20px' }}>
            <button
              className="btn btn-primary"
              onClick={connectWebSocket}
              disabled={connected || isConnecting}
              aria-label="Connect to Gesture WebSocket"
              style={{
                padding: '8px 16px',
                border: 'none',
                borderRadius: '4px',
                cursor: connected || isConnecting ? 'not-allowed' : 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                fontSize: '14px',
                backgroundColor: connected ? '#4caf50' : isConnecting ? '#9e9e9e' : '#2196F3',
                color: 'white',
                opacity: connected || isConnecting ? 0.6 : 1
              }}
            >
              <MdLink style={{ verticalAlign: 'middle', marginRight: 4 }} />
              {connected ? 'Connected' : isConnecting ? 'Connecting...' : 'Connect Gesture'}
            </button>

            <div className={`connection-status ${connected ? 'connected' : 'disconnected'}`} style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '14px',
              padding: '4px 12px',
              borderRadius: '12px',
              background: '#f5f5f5'
            }}>
              <span className="status-dot" style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                display: 'inline-block',
                backgroundColor: connected ? '#4caf50' : '#f44336'
              }}></span>
              <span className="status-text">
                {connected ? 'Gesture Connected' : 'Gesture Disconnected'}
              </span>
            </div>

            {connectionError && <p className="connection-error" style={{
              color: '#f44336',
              marginLeft: '12px',
              fontSize: '13px'
            }}>{connectionError}</p>}
          </div>

          {prediction && (
            <div className="prediction-container" style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid #eee' }}>
              <h3 style={{ marginBottom: '10px', color: '#333' }}>Gesture Prediction Result:</h3>
              <div className="prediction-result" style={{
                background: '#f9f9f9',
                padding: '15px',
                borderRadius: '4px',
                marginTop: '10px',
                overflowX: 'auto',
                fontFamily: 'Courier New, monospace',
                fontSize: '14px'
              }}>
                <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
                  {typeof prediction === 'string' ? prediction : JSON.stringify(prediction, null, 2)}
                </pre>
              </div>
            </div>
          )}

          <style jsx>{`
            @keyframes pulse {
              0% { transform: scale(1); opacity: 1; }
              50% { transform: scale(1.2); opacity: 0.7; }
              100% { transform: scale(1); opacity: 1; }
            }
          `}</style>
        </div>
      </div>
    </div>
  );
};

export default LivePredict;