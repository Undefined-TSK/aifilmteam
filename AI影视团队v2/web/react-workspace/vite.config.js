import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/react/',
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8190',
        changeOrigin: true,
      },
      '/project-assets': {
        target: 'http://127.0.0.1:8190',
        changeOrigin: true,
      },
      '/k13-assets': {
        target: 'http://127.0.0.1:8190',
        changeOrigin: true,
      },
    },
  },
})
