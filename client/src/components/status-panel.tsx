import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { CheckCircle, AlertTriangle, Pause, Loader2 } from "lucide-react";

interface StatusPanelProps {
  status: 'idle' | 'running' | 'completed' | 'error';
  progress?: number;
  message?: string;
  stats?: {
    processed: number;
    remaining: number;
    errors: number;
    eta: string;
  };
  errorMessage?: string;
}

export function StatusPanel({ 
  status, 
  progress = 0, 
  message = "", 
  stats, 
  errorMessage 
}: StatusPanelProps) {
  const renderStatusContent = () => {
    switch (status) {
      case 'idle':
        return (
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-slate-100 rounded-full flex items-center justify-center">
              <Pause className="h-4 w-4 text-slate-400" />
            </div>
            <div>
              <p className="font-medium text-slate-700">Ready to scrape</p>
              <p className="text-sm text-slate-500">Select a batch and click "Start Scraping" to begin</p>
            </div>
          </div>
        );

      case 'running':
        return (
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                <Loader2 className="h-4 w-4 text-white animate-spin" />
              </div>
              <div>
                <p className="font-medium text-slate-700">Scraping in progress...</p>
                <p className="text-sm text-slate-500">{message || "Processing batch"}</p>
              </div>
            </div>
            
            <Progress value={progress} className="mb-4" />
            
            {stats && (
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-center">
                <div className="bg-slate-50 rounded-lg p-3">
                  <div className="text-lg font-semibold text-slate-900">{stats.processed}</div>
                  <div className="text-xs text-slate-500">Processed</div>
                </div>
                <div className="bg-slate-50 rounded-lg p-3">
                  <div className="text-lg font-semibold text-slate-900">{stats.remaining}</div>
                  <div className="text-xs text-slate-500">Remaining</div>
                </div>
                <div className="bg-slate-50 rounded-lg p-3">
                  <div className="text-lg font-semibold text-slate-900">{stats.errors}</div>
                  <div className="text-xs text-slate-500">Errors</div>
                </div>
                <div className="bg-slate-50 rounded-lg p-3">
                  <div className="text-lg font-semibold text-slate-900">{stats.eta}</div>
                  <div className="text-xs text-slate-500">ETA</div>
                </div>
              </div>
            )}
          </div>
        );

      case 'completed':
        return (
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-success rounded-full flex items-center justify-center">
              <CheckCircle className="h-4 w-4 text-white" />
            </div>
            <div>
              <p className="font-medium text-slate-700">Scraping completed successfully</p>
              <p className="text-sm text-slate-500">{message || "All companies processed"}</p>
            </div>
          </div>
        );

      case 'error':
        return (
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-error rounded-full flex items-center justify-center">
              <AlertTriangle className="h-4 w-4 text-white" />
            </div>
            <div>
              <p className="font-medium text-slate-700">Scraping failed</p>
              <p className="text-sm text-slate-500">{errorMessage || "An error occurred during scraping"}</p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Scraping Status</CardTitle>
      </CardHeader>
      <CardContent>
        {renderStatusContent()}
      </CardContent>
    </Card>
  );
}
