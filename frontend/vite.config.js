import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxies /api requests to the Flask backend during development so the
// frontend can just call fetch("/api/...") without worrying about CORS
// or hardcoding a host.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
    },
  },
});
