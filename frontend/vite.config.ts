import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// En desarrollo, /api/* se reenvía al backend FastAPI (sin problemas de CORS).
export default defineConfig(({ command }) => ({
  base: command === "build" ? "/static/" : "/",
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true, rewrite: (p) => p.replace(/^\/api/, "") },
    },
  },
  build: {
    outDir: "../backend/static",
    emptyOutDir: true,
  },
}));
