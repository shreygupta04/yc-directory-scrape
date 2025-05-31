import express from "express";
import { registerRoutes } from "./routes";

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

let cachedServer: any = null;

const initServer = async () => {
  if (!cachedServer) {
    const httpServer = await registerRoutes(app);
    cachedServer = httpServer;
  }
  return cachedServer;
};

// This is the Vercel-compatible entrypoint
export default async function handler(req, res) {
  const server = await initServer();
  server.emit("request", req, res);
}
