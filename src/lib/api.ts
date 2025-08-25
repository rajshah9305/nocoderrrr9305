// src/lib/api.ts
import axios from 'axios'
export const api = axios.create({
  baseURL: '/api', // works with Vite proxy and prod if you set NGiNX/rewrites
})
