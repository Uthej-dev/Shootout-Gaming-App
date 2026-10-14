import axios from 'axios';
import { API_BASE_URL } from '../constants/config';

let token = null;
let onUnauthorized = null;
export const setAuthToken = (t) => { token = t; };
export const setUnauthorizedHandler = (fn) => { onUnauthorized = fn; };

const api = axios.create({ baseURL: API_BASE_URL, timeout: 15000 });

api.interceptors.request.use((cfg) => {
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

// Resolves to the backend envelope {success, data, message}; rejects with {status, code, message, details}.
api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const d = err.response?.data;
    const e = {
      status: err.response?.status,
      code: d?.code || (err.response ? 'ERROR' : 'NETWORK_ERROR'),
      message: d?.message || (err.response ? 'Something went wrong' : 'Cannot reach the server. Check your connection.'),
      details: d?.details,
    };
    if (e.status === 401 && token && onUnauthorized) onUnauthorized();
    return Promise.reject(e);
  }
);

export default api;
