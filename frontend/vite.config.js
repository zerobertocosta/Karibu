// frontend/vite.config.js
import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173, // A porta do seu servidor frontend Vue
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // <-- Mantenha este
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api'), // <-- DESCOMENTE ESTA LINHA
      }
    }
  }
})