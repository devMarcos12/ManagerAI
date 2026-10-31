import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const target = env.MANAGERAI_PROXY_TARGET || 'http://127.0.0.1:8011';
  const proxy = { '/v1': { target, changeOrigin: false } };
  return { plugins: [react()], server: { host: '127.0.0.1', port: 5173, strictPort: true, proxy },
    preview: { host: '127.0.0.1', port: 4173, strictPort: true, proxy } };
});
