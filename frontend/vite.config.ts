import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  // In production the Python server serves the built files,
  // so we don't need a base URL prefix.
  base: "/",
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
  server: {
    // Dev server proxy: forward /ws to the Python backend
    proxy: {
      "/ws": {
        target:    "ws://127.0.0.1:7410",
        ws:        true,
        changeOrigin: true,
      },
    },
  },
});
