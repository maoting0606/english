import axios from 'axios'
export const api = axios.create({ baseURL: '/api/v1' })
export const parseText = (text, title = '粘贴文本') => api.post('/parse/text', { text, title })
export const createDocument = (text, title = '粘贴文本') => api.post('/doc/create', { text, title })
export const uploadDocument = (formData) => api.post('/doc/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
export const uploadOcrImage = (formData) => api.post('/ocr/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
export const listDocuments = () => api.get('/doc/list')
export const searchWord = (query) => api.post('/word/search', { query })
