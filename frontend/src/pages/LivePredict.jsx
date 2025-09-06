import React, { useState, useRef, useEffect, useCallback } from "react";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const WS_URL = "ws://localhost:8000/ws/stream";

const LivePredict = () => {
  const [prediction, setPrediction] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [connected, setConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [ttsEnabled, setTtsEnabled] = useState(false);
  const [isTtsSupported, setIsTtsSupported] = useState(false);

  const wsRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const reconnectTimeout = useRef(null);

  const ttsQueue = useRef([]);
  const utteranceRef = useRef(null);
  const lastSpokenPrediction = useRef(null);
  const resetTimeout = useRef(null);
  const lastTtsTime = useRef(0);

  // --- TTS Support ---
  useEffect(() => {
    const supported = "speechSynthesis" in window;
    setIsTtsSupported(supported);
    if (supported) window.speechSynthesis.getVoices();
  }, []);

  const speakNextInQueue = useCallback(() => {
    if (!ttsEnabled || ttsQueue.current.length === 0) return;

    const text = ttsQueue.current.shift();
    if (!text) return;

    if (window.speechSynthesis.speaking) window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = 0.9;

    utterance.onend = () => speakNextInQueue();
    utterance.onerror = () => speakNextInQueue();

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  }, [ttsEnabled]);

  const enqueuePrediction = useCallback(
    (text) => {
      if (!text) return;
      const now = Date.now();

      if (text === lastSpokenPrediction.current) return;
      if (now - lastTtsTime.current < 400) return;

      lastSpokenPrediction.current = text;
      lastTtsTime.current = now;
      ttsQueue.current.push(text);
      if (!window.speechSynthesis.speaking) speakNextInQueue();
    },
    [speakNextInQueue]
  );

  const enableTTS = useCallback(() => {
    if (!isTtsSupported) return toast.error("Browser does not support TTS");
    setTtsEnabled((prev) => !prev);
    toast.info(!ttsEnabled ? "TTS Enabled" : "TTS Disabled");
  }, [isTtsSupported, ttsEnabled]);

  // --- WebSocket connection with auto-reconnect ---
  const connectWebSocket = useCallback(() => {
    if (isConnecting) return;

    setIsConnecting(true);
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("Connected to WebSocket:", WS_URL);
      setConnected(true);
      setIsConnecting(false);
      reconnectAttempts.current = 0; // reset attempts
      toast.success("Connected to live predictions!");
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.prediction) {
          setPrediction(data.prediction);
          setConfidence(data.confidence || null);
          if (ttsEnabled) enqueuePrediction(data.prediction);
        }

        clearTimeout(resetTimeout.current);
        resetTimeout.current = setTimeout(() => {
          lastSpokenPrediction.current = null;
        }, 2000);
      } catch (err) {
        console.error("WebSocket parse error:", err, "Raw:", event.data);
      }
    };

    const handleCloseOrError = (reason) => {
      console.warn("WebSocket closed/error:", reason);
      setConnected(false);
      setIsConnecting(false);

      // Exponential backoff for reconnect
      const attempt = reconnectAttempts.current++;
      const delay = Math.min(1000 * 2 ** attempt, 30000); // cap at 30s
      console.log(`Reconnecting in ${delay / 1000}s (attempt ${attempt + 1})...`);

      reconnectTimeout.current = setTimeout(() => {
        connectWebSocket();
      }, delay);
    };

    ws.onclose = () => handleCloseOrError("closed");
    ws.onerror = () => handleCloseOrError("error");
  }, [isConnecting, ttsEnabled, enqueuePrediction]);

  const resetPrediction = useCallback(() => {
    setPrediction(null);
    setConfidence(null);
    lastSpokenPrediction.current = null;
  }, []);

  // --- Cleanup ---
  useEffect(() => {
    return () => {
      window.speechSynthesis.cancel();
      if (wsRef.current) wsRef.current.close();
      clearTimeout(resetTimeout.current);
      clearTimeout(reconnectTimeout.current);
    };
  }, []);

  return (
    <div className="max-w-md mx-auto mt-10 p-6 bg-white rounded-xl shadow-md text-center">
      <h2 className="text-2xl font-bold mb-4 text-blue-600">Live Gesture Prediction</h2>

      <div className="flex flex-wrap justify-center gap-3 mb-6">
        <button
          onClick={connectWebSocket}
          disabled={connected || isConnecting}
          className={`px-4 py-2 rounded ${
            connected
              ? "bg-green-500 text-white cursor-not-allowed"
              : isConnecting
              ? "bg-yellow-400 text-white cursor-wait"
              : "bg-blue-500 text-white hover:bg-blue-600"
          }`}
        >
          {connected ? "Connected" : isConnecting ? "Connecting..." : "Connect"}
        </button>

        <button
          onClick={enableTTS}
          disabled={!isTtsSupported}
          className={`px-4 py-2 rounded ${
            ttsEnabled ? "bg-purple-500 text-white" : "bg-gray-300 text-gray-700"
          }`}
        >
          {ttsEnabled ? "TTS Enabled" : "TTS Disabled"}
        </button>

        <button
          onClick={() => prediction && enqueuePrediction(prediction)}
          disabled={!prediction || !ttsEnabled}
          className="px-4 py-2 rounded bg-indigo-500 text-white hover:bg-indigo-600"
        >
          Speak Now
        </button>

        <button
          onClick={resetPrediction}
          disabled={!prediction}
          className="px-4 py-2 rounded bg-red-500 text-white hover:bg-red-600"
        >
          Reset
        </button>
      </div>

      {prediction ? (
        <div className="mb-4">
          <p className="text-xl font-semibold mb-1">{prediction}</p>
          {confidence !== null && (
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div
                className="bg-green-500 h-4 rounded-full"
                style={{ width: `${Math.min(confidence * 100, 100)}%` }}
              ></div>
            </div>
          )}
        </div>
      ) : (
        <p className="text-gray-500 mb-4">Waiting for live predictions...</p>
      )}

      <h4 className="text-lg font-medium mb-2">Pending TTS Queue</h4>
      {ttsQueue.current.length === 0 ? (
        <p className="text-gray-400">No pending predictions</p>
      ) : (
        <ul className="list-none p-0">
          {ttsQueue.current.map((item, index) => (
            <li
              key={index}
              className="bg-blue-100 mb-1 px-3 py-1 rounded text-sm text-blue-800"
            >
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default LivePredict;
