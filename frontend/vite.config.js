import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
<<<<<<< HEAD
        target: 'http://127.0.0.1:5000',
=======
        target: 'http://localhost:5000',
>>>>>>> c3921a9d5b68613776360a1327f9c5d1df6972d8
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
})
