import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Header } from "@/components/header";
import { ControlPanel } from "@/components/control-panel";
import { StatusPanel } from "@/components/status-panel";
import { SpreadsheetViewer } from "@/components/spreadsheet-viewer";
import { useWebSocket } from "@/hooks/use-websocket";

export default function Home() {
  const [currentJob, setCurrentJob] = useState<any>(null);
  const [jobStatus, setJobStatus] = useState<'idle' | 'running' | 'completed' | 'error'>('idle');
  const [progress, setProgress] = useState(0);
  const [stats, setStats] = useState<any>(null);
  const [statusMessage, setStatusMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const { data: jobs } = useQuery({
    queryKey: ["/api/scrape-jobs"],
    refetchInterval: 5000,
  });

  const { isConnected } = useWebSocket((message) => {
    switch (message.type) {
      case 'job_update':
        if (message.status === 'running') {
          setJobStatus('running');
          setProgress(0);
          setStatusMessage("Starting scrape process...");
        }
        break;
        
      case 'progress_update':
        setProgress(message.progress || 0);
        setStats({
          processed: message.processed || 0,
          remaining: (message.total || 0) - (message.processed || 0),
          errors: message.errors || 0,
          eta: message.eta || "~--"
        });
        setStatusMessage(`Processing companies...`);
        break;
        
      case 'job_completed':
        setJobStatus('completed');
        setProgress(100);
        setStatusMessage(`Processed ${message.companiesProcessed} companies successfully`);
        break;
        
      case 'job_error':
        setJobStatus('error');
        setErrorMessage(message.error || "Unknown error occurred");
        break;
    }
  });

  // Get the most recent job to determine initial status
  useEffect(() => {
    if (jobs && jobs.length > 0) {
      const latestJob = jobs[0];
      setCurrentJob(latestJob);
      
      if (latestJob.status === 'running') {
        setJobStatus('running');
        setProgress(latestJob.progress || 0);
        setStats({
          processed: latestJob.processedCompanies || 0,
          remaining: (latestJob.totalCompanies || 0) - (latestJob.processedCompanies || 0),
          errors: latestJob.errorCount || 0,
          eta: "~--"
        });
      } else if (latestJob.status === 'completed') {
        setJobStatus('completed');
        setProgress(100);
        setStatusMessage(`Processed ${latestJob.processedCompanies} companies from ${latestJob.batch} batch`);
      } else if (latestJob.status === 'error') {
        setJobStatus('error');
        setErrorMessage(latestJob.errorMessage || "Unknown error");
      }
    }
  }, [jobs]);

  const getLastRunTime = () => {
    if (!jobs || jobs.length === 0) return "Never";
    
    const lastJob = jobs.find(job => job.status === 'completed');
    if (!lastJob || !lastJob.completedAt) return "Never";
    
    const completedTime = new Date(lastJob.completedAt);
    const now = new Date();
    const diffMs = now.getTime() - completedTime.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
    if (diffHours > 0) {
      return `${diffHours}h ago`;
    } else {
      const diffMinutes = Math.floor(diffMs / (1000 * 60));
      return diffMinutes > 0 ? `${diffMinutes}m ago` : "Just now";
    }
  };

  return (
    <div className="bg-slate-50 min-h-screen">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <ControlPanel lastRun={getLastRunTime()} />
        </div>

        <div className="mb-8">
          <StatusPanel
            status={jobStatus}
            progress={progress}
            message={statusMessage}
            stats={stats}
            errorMessage={errorMessage}
          />
        </div>

        <div className="mb-8">
          <SpreadsheetViewer />
        </div>
      </div>
    </div>
  );
}
