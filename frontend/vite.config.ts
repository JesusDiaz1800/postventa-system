import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [
      react()
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom'],
  },
  server: {
<<<<<<< HEAD
    port: 3000,
    host: '0.0.0.0',
    hmr: {
      port: 3001,
      host: 'localhost',
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
=======
    port: 5173,
    host: '0.0.0.0',
    hmr: {
      port: 5174,
      host: '192.168.1.234',
    },
    proxy: {
      '/api': {
        target: 'http://192.168.1.234:8000',
>>>>>>> 674c244 (tus cambios)
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});