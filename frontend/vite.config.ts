import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/auth": "http://localhost:8000",
      "/workflow": "http://localhost:8000",
      "/reviews": "http://localhost:8000",
      "/patients": "http://localhost:8000",
      "/documents": "http://localhost:8000",
      "/integrations": "http://localhost:8000",
      "/demo": "http://localhost:8000",
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
  },
});
