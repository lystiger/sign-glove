import axios from 'axios';

const BASE_URL = 'http://localhost:8080';

export async function apiRequest(method, url, data = null, config = {}) {
  try {
    const res = await axios({
      method,
      url: BASE_URL + url,
      data,
      ...config,
    });
    return res.data;
  } catch (err) {
    // Extract error message and trace_id if available
    const detail = err.response?.data?.detail || err.message;
    const traceId = err.response?.data?.trace_id;
    throw { detail, traceId, status: err.response?.status };
  }
}

// Example API functions for gestures
export const getGestures = () => apiRequest('get', '/gestures');
export const createGesture = (payload) => apiRequest('post', '/gestures/', payload);
export const deleteGesture = (sessionId) => apiRequest('delete', `/gestures/${sessionId}`);
export const updateGesture = (sessionId, label) => apiRequest('put', `/gestures/${sessionId}?label=${label}`); 