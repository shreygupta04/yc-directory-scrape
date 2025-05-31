import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ExternalLink, RotateCcw } from "lucide-react";

interface SpreadsheetViewerProps {
  spreadsheetUrl?: string;
}

export function SpreadsheetViewer({ 
  spreadsheetUrl = "https://docs.google.com/spreadsheets/d/1jFLtlpbTBKzSEsThdD9tfP8AQr-_TIPOrVWMjr_Zl50/edit?usp=sharing&widget=true&headers=false"
}: SpreadsheetViewerProps) {
  const [isLoading, setIsLoading] = useState(true);

  const handleOpenInNewTab = () => {
    const editUrl = spreadsheetUrl.replace('&widget=true&headers=false', '');
    window.open(editUrl, '_blank');
  };

  const handleRefresh = () => {
    setIsLoading(true);
    // Force iframe refresh by changing the src
    const iframe = document.querySelector('#sheets-iframe') as HTMLIFrameElement;
    if (iframe) {
      const currentSrc = iframe.src;
      iframe.src = '';
      setTimeout(() => {
        iframe.src = currentSrc;
      }, 100);
    }
  };

  return (
    <Card className="overflow-hidden">
      <CardHeader className="border-b border-slate-200">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Company Data</CardTitle>
            <p className="text-sm text-slate-600 mt-1">
              Live view of the Google Spreadsheet with scraped company information
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 text-sm text-slate-500">
              <RotateCcw className="h-4 w-4" />
              <span>Auto-refresh</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleRefresh}
              className="text-sm text-slate-600 hover:text-slate-900"
            >
              <RotateCcw className="h-4 w-4 mr-1" />
              Refresh
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleOpenInNewTab}
              className="text-sm text-primary hover:text-blue-700"
            >
              <ExternalLink className="h-4 w-4 mr-1" />
              Open in Sheets
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="p-0">
        <div className="relative" style={{ height: '600px' }}>
          <iframe
            id="sheets-iframe"
            src={spreadsheetUrl}
            className="w-full h-full border-0"
            onLoad={() => setIsLoading(false)}
          />
          
          {isLoading && (
            <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center">
              <div className="text-center">
                <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-2"></div>
                <p className="text-sm text-slate-600">Loading spreadsheet...</p>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
