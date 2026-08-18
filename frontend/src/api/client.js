import axios from 'axios'
export const api = axios.create({ baseURL: '/api/v1' })
export const parseText = (text) => api.post('/parse/text', { text })
export const createDocument = (text) => api.post('/doc/create', { text })
export const searchWord = (query) => api.post('/word/search', { query })
