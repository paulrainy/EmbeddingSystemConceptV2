// src/api.ts
import axios from 'axios';

/**
 * Единая точка входа для всех запросов к FastAPI-серверу.
 * Адрес берём из переменной окружения VITE_API_BASE,
 * чтобы всё работало и локально, и на staging/production.
 */
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000',
  timeout: 10_000,
});
