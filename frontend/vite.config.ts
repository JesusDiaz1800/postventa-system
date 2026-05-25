import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import fs from 'fs';

// SSL certificate paths
const sslDir = path.resolve(process.cwd(), 'ssl');
const keyPath = path.join(sslDir, 'key.pem');
const certPath = path.join(sslDir, 'cert.pem');
const hasSSL = fs.existsSync(keyPath) && fs.existsSync(certPath);

export default defineConfig({
  base: '/',
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve('./src'),
    },
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom', '@tanstack/react-query'],
  },
  server: {
    port: 5174,
    host: '0.0.0.0',
    strictPort: true,
    allowedHosts: ['sertec.polifusion.com'],
    hmr: {
      overlay: true,
      clientPort: 443,
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        secure: false,
        timeout: 600000,
      },
      '/ws': {
        target: 'http://127.0.0.1:8001',
        ws: true,
        secure: false,
        changeOrigin: false,
      },
      '/documentos': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'esbuild',
    target: 'es2015',
    cssCodeSplit: true,
    assetsInlineLimit: 4096, // inline assets < 4KB as base64
    rollupOptions: {
      output: {
        // Fine-grained code splitting for better caching
        manualChunks(id) {
          // Core React runtime — smallest, most cached chunk
          if (id.includes('node_modules/react/') || id.includes('node_modules/react-dom/')) {
            return 'react-core';
          }
          // Router
          if (id.includes('node_modules/react-router-dom') || id.includes('node_modules/react-router/') || id.includes('node_modules/@remix-run/')) {
            return 'router';
          }
          // Data fetching
          if (id.includes('node_modules/@tanstack/')) {
            return 'tanstack';
          }
          // Animation library (heavy — isolate so it caches independently)
          if (id.includes('node_modules/framer-motion')) {
            return 'framer-motion';
          }
          // Icons (large)
          if (id.includes('node_modules/@heroicons/') || id.includes('node_modules/lucide-react')) {
            return 'icons';
          }
          // Toast notifications
          if (id.includes('node_modules/react-hot-toast')) {
            return 'ui-utils';
          }
        },
        // Cache-friendly filenames with content hash
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
      },
    },
    chunkSizeWarningLimit: 800,
  },
});