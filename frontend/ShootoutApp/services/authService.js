import api from './api';

export const login = (identifier, password) => api.post('/auth/login', { identifier, password }).then((r) => r.data);
export const register = (p) => api.post('/auth/register', p).then((r) => r.data);
export const forgotPassword = (identifier) => api.post('/auth/forgot-password', { identifier }).then((r) => r.message);
