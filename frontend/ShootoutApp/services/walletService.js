import api from './api';

export const getWallet = () => api.get('/wallet').then((r) => r.data);
export const getTransactions = () => api.get('/wallet/transactions').then((r) => r.data);
