import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";
import fs from "fs";

function uploadMiddleware() {
  return {
    name: "file-upload-middleware",
    configureServer(server) {
      server.middlewares.use("/api/upload", (req, res, next) => {
        if (req.method === "POST") {
          let filename = req.headers["x-file-name"] || "uploaded_file";
          filename = decodeURIComponent(filename);

          const uploadDir = path.resolve(__dirname, "../../data");
          if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
          }

          const filePath = path.join(uploadDir, filename);
          const writeStream = fs.createWriteStream(filePath);

          req.pipe(writeStream);

          req.on("end", () => {
            res.statusCode = 200;
            res.setHeader("Content-Type", "application/json");
            res.end(
              JSON.stringify({ message: "Upload successful", path: filePath }),
            );
          });

          writeStream.on("error", (err) => {
            console.error("Write error:", err);
            res.statusCode = 500;
            res.end(JSON.stringify({ error: err.message }));
          });
        } else {
          next();
        }
      });
    },
  };
}

export default defineConfig({
  plugins: [react(), tailwindcss(), uploadMiddleware()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: "0.0.0.0",
    proxy: {
      "/process-csv": "http://backend:8000",
    },
  },
});
