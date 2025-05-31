import type { Express } from "express";
import { createServer, type Server } from "http";
import { WebSocketServer, WebSocket } from "ws";
import { storage } from "./storage";
import { insertScrapeJobSchema } from "@shared/schema";
import { runPythonScraper } from "./python-runner";

export async function registerRoutes(app: Express): Promise<Server> {
  const httpServer = createServer(app);
  
  // WebSocket server for real-time updates
  const wss = new WebSocketServer({ server: httpServer, path: '/ws' });
  
  // Store WebSocket connections
  const wsClients = new Set<WebSocket>();
  
  wss.on('connection', (ws) => {
    wsClients.add(ws);
    
    ws.on('close', () => {
      wsClients.delete(ws);
    });
  });
  
  // Broadcast update to all connected clients
  function broadcastUpdate(data: any) {
    wsClients.forEach(ws => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(data));
      }
    });
  }

  // Get all scrape jobs
  app.get("/api/scrape-jobs", async (req, res) => {
    try {
      const jobs = await storage.getAllScrapeJobs();
      res.json(jobs);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch scrape jobs" });
    }
  });

  // Get specific scrape job
  app.get("/api/scrape-jobs/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const job = await storage.getScrapeJob(id);
      
      if (!job) {
        return res.status(404).json({ message: "Scrape job not found" });
      }
      
      res.json(job);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch scrape job" });
    }
  });

  // Create new scrape job
  app.post("/api/scrape-jobs", async (req, res) => {
    try {
      const validatedData = insertScrapeJobSchema.parse(req.body);
      const job = await storage.createScrapeJob(validatedData);
      
      // Start the scraping process asynchronously
      runScrapeJob(job.id, broadcastUpdate);
      
      res.status(201).json(job);
    } catch (error) {
      res.status(400).json({ message: "Invalid scrape job data" });
    }
  });

  // Get company statistics
  app.get("/api/stats", async (req, res) => {
    try {
      const stats = await storage.getCompanyStats();
      res.json(stats);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch statistics" });
    }
  });

  // Get companies by batch
  app.get("/api/companies/:batch", async (req, res) => {
    try {
      const batch = req.params.batch;
      const companies = await storage.getCompaniesByBatch(batch);
      res.json(companies);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch companies" });
    }
  });

  async function runScrapeJob(jobId: number, broadcast: (data: any) => void) {
    try {
      const job = await storage.getScrapeJob(jobId);
      if (!job) return;

      // Update job status to running
      await storage.updateScrapeJob(jobId, { 
        status: "running",
        progress: 0 
      });
      
      broadcast({
        type: 'job_update',
        jobId,
        status: 'running',
        progress: 0
      });

      // Run the Python scraper
      const result = await runPythonScraper(job.batch, job.mode, (progress) => {
        // Update progress in storage
        storage.updateScrapeJob(jobId, {
          progress: progress.percentage,
          processedCompanies: progress.processed,
          totalCompanies: progress.total,
          errorCount: progress.errors
        });

        // Broadcast progress update
        broadcast({
          type: 'progress_update',
          jobId,
          progress: progress.percentage,
          processed: progress.processed,
          total: progress.total,
          errors: progress.errors,
          eta: progress.eta
        });
      });

      // Update job as completed
      await storage.updateScrapeJob(jobId, {
        status: "completed",
        progress: 100,
        completedAt: new Date()
      });

      // Store the scraped companies
      for (const company of result.companies) {
        await storage.createCompany(company);
      }

      broadcast({
        type: 'job_completed',
        jobId,
        companiesProcessed: result.companies.length
      });

    } catch (error) {
      // Update job with error
      await storage.updateScrapeJob(jobId, {
        status: "error",
        errorMessage: error instanceof Error ? error.message : "Unknown error occurred",
        completedAt: new Date()
      });

      broadcast({
        type: 'job_error',
        jobId,
        error: error instanceof Error ? error.message : "Unknown error occurred"
      });
    }
  }

  return httpServer;
}
