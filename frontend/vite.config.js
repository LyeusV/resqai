import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling: true,    // ← Docker'da dosya değişikliklerini polling ile izle
      interval: 300,       // ← 300ms'de bir kontrol et
    },
    hmr: {
      host: 'localhost',   // ← Tarayıcının bağlanacağı host
    },
  },
})