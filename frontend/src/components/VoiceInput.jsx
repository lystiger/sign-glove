import { useState } from 'react';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const VoiceInput = ({ onVoiceRecognized, disabled = false }) => {
  const [isListening, setIsListening] = useState(false);

  const handleVoiceInput = async () => {
    if (disabled) {
      toast.warning('Voice input is disabled. Please connect first.');
      return;
    }
    
    setIsListening(true);
    const toastId = toast.loading('🎤 Initializing microphone...');
    
    try {
      const response = await fetch('http://localhost:8000/api/voice/manual', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.detail || 'Voice recognition failed');
      }

      if (result.text) {
        toast.update(toastId, {
          render: '✅ Voice recognized!',
          type: 'success',
          isLoading: false,
          autoClose: 3000,
        });
        onVoiceRecognized(result.text);
      } else {
        throw new Error('No text was recognized');
      }
      
    } catch (error) {
      console.error('Voice recognition error:', error);
      
      toast.update(toastId, {
        render: `❌ ${error.message || 'Failed to recognize voice'}`,
        type: 'error',
        isLoading: false,
        autoClose: 5000,
      });
      
    } finally {
      setIsListening(false);
    }
  };

  return (
    <button
      onClick={handleVoiceInput}
      disabled={disabled || isListening}
      className={`voice-button ${isListening ? 'listening' : ''} ${disabled ? 'disabled' : ''}`}
      aria-label={isListening ? 'Listening...' : 'Start voice input'}
      title={isListening ? 'Listening...' : 'Click to speak'}
    >
      <span className="button-icon">
        {isListening ? (
          <span className="pulse-animation">
            <i className="fas fa-microphone"></i>
          </span>
        ) : (
          <i className="fas fa-microphone"></i>
        )}
      </span>
      <style jsx>{`
        .voice-button {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 12px 24px;
          font-size: 16px;
          border: none;
          border-radius: 50px;
          background: #4CAF50;
          color: white;
          cursor: pointer;
          margin: 10px;
          transition: all 0.3s ease;
          box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        
        .voice-button:hover:not(:disabled) {
          background: #45a049;
          transform: translateY(-2px);
          box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        
        .voice-button:active:not(:disabled) {
          transform: translateY(0);
        }
        
        .voice-button:disabled {
          background: #cccccc;
          cursor: not-allowed;
          opacity: 0.7;
        }
        
        .voice-button.listening {
          background: #f57c00;
        }
        
        .pulse-animation {
          animation: pulse 1.5s infinite;
          display: inline-block;
        }
        
        @keyframes pulse {
          0% { transform: scale(1); }
          50% { transform: scale(1.2); }
          100% { transform: scale(1); }
        }
        
        .button-icon {
          display: inline-flex;
          align-items: center;
        }
      `}</style>
    </button>
  );
};

export default VoiceInput;
