import api from './api';

export const listByGame = (game, status) =>
  api.get(status ? `/matches/${game}/${status}` : `/matches/${game}`).then((r) => r.data);
export const join = (matchId) => api.post(`/matches/${matchId}/join`).then((r) => r.data);
export const getRoom = (matchId) => api.get(`/matches/${matchId}/room`).then((r) => r.data);
