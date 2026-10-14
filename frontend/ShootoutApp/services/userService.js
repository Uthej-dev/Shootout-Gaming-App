import api from './api';

export const me = () => api.get('/users/me').then((r) => r.data);
export const joinedMatches = () => api.get('/users/me/joined-matches').then((r) => r.data);
