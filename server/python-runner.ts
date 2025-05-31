import { spawn } from "child_process";
import path from "path";

export interface ScrapeProgress {
  percentage: number;
  processed: number;
  total: number;
  errors: number;
  eta: string;
  message: string;
}

export interface ScrapeResult {
  companies: Array<{
    companyName: string;
    batch: string;
    description: string;
    website: string;
    geo: string;
    founders: any;
    notes?: string;
  }>;
  totalProcessed: number;
  errors: number;
}

export async function runPythonScraper(
  batch: string,
  mode: string,
  onProgress: (progress: ScrapeProgress) => void
): Promise<ScrapeResult> {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(process.cwd(), "attached_assets", "main.py");
    
    // Spawn Python process
    const pythonProcess = spawn("python3", [scriptPath, batch], {
      stdio: ["pipe", "pipe", "pipe"],
      env: {
        ...process.env,
        SCRAPE_MODE: mode,
        BATCH: batch
      }
    });

    let output = "";
    let errorOutput = "";
    let processed = 0;
    let total = 0;
    let errors = 0;

    pythonProcess.stdout.on("data", (data) => {
      const chunk = data.toString();
      output += chunk;
      
      // Parse progress updates from Python script output
      const lines = chunk.split("\n");
      for (const line of lines) {
        if (line.includes("PROGRESS:")) {
          try {
            const progressData = JSON.parse(line.replace("PROGRESS:", ""));
            processed = progressData.processed || processed;
            total = progressData.total || total;
            errors = progressData.errors || errors;
            
            const percentage = total > 0 ? Math.round((processed / total) * 100) : 0;
            const remainingTime = calculateETA(processed, total);
            
            onProgress({
              percentage,
              processed,
              total,
              errors,
              eta: remainingTime,
              message: progressData.message || `Processing ${batch} batch`
            });
          } catch (e) {
            // Ignore JSON parsing errors for non-progress lines
          }
        }
      }
    });

    pythonProcess.stderr.on("data", (data) => {
      errorOutput += data.toString();
    });

    pythonProcess.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(`Python script failed with code ${code}: ${errorOutput}`));
        return;
      }

      try {
        // Parse the final result from Python script
        const lines = output.split("\n");
        const resultLine = lines.find(line => line.includes("RESULT:"));
        
        if (resultLine) {
          const result = JSON.parse(resultLine.replace("RESULT:", ""));
          resolve({
            companies: result.companies || [],
            totalProcessed: processed,
            errors
          });
        } else {
          // Fallback: try to parse the entire output as JSON
          const result = JSON.parse(output);
          resolve({
            companies: Array.isArray(result) ? result : [],
            totalProcessed: processed,
            errors
          });
        }
      } catch (error) {
        reject(new Error(`Failed to parse Python script output: ${error}`));
      }
    });

    pythonProcess.on("error", (error) => {
      reject(new Error(`Failed to start Python script: ${error.message}`));
    });
  });
}

function calculateETA(processed: number, total: number): string {
  if (processed === 0 || total === 0) return "~--";
  
  const rate = processed / total;
  const remaining = total - processed;
  const secondsRemaining = remaining / (rate * processed);
  
  if (secondsRemaining < 60) {
    return `~${Math.round(secondsRemaining)}s`;
  } else if (secondsRemaining < 3600) {
    return `~${Math.round(secondsRemaining / 60)}m`;
  } else {
    return `~${Math.round(secondsRemaining / 3600)}h`;
  }
}
