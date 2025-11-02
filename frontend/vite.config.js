import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        // When running in Docker, use the backend service name
        // When running locally, use localhost:43798
        target: process.env.DOCKER_ENV ? 'http://backend:5000' : 'http://localhost:43798',
        changeOrigin: true,
      },
    },
  },
})
