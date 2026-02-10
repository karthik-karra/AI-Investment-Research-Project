// src/services/api.js
import axios from 'axios';

const apiService = axios.create({
  baseURL: 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

export default apiService;