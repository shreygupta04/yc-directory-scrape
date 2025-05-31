import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Play, Clock } from "lucide-react";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";

interface ControlPanelProps {
  lastRun?: string;
}

export function ControlPanel({ lastRun = "Never" }: ControlPanelProps) {
  const [batch, setBatch] = useState("");
  const [mode, setMode] = useState("full");
  
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const startScrapeMutation = useMutation({
    mutationFn: async (data: { batch: string; mode: string; options: any }) => {
      const response = await apiRequest("POST", "/api/scrape-jobs", data);
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Scraping Started",
        description: "The scraping job has been queued and will begin shortly.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/scrape-jobs"] });
    },
    onError: (error) => {
      toast({
        title: "Failed to Start Scraping",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!batch) {
      toast({
        title: "Batch Required",
        description: "Please input a batch to scrape.",
        variant: "destructive",
      });
      return;
    }

    const batchPattern = /^(Winter|Summer|Spring|Fall) 20\d{2}$/;
    if (!batchPattern.test(batch)) {
      toast({
        title: "Invalid Batch Format",
        description: "Please enter a valid batch in the format 'Season YYYY' (e.g. 'Winter 2025').",
        variant: "destructive",
      });
      return;
    }
    
    const options = {};

    startScrapeMutation.mutate({ batch, mode, options });
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Scraping Controls</CardTitle>
            <CardDescription>
              Select a YC batch to scrape and update the spreadsheet
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2 text-sm text-slate-500">
            <Clock className="h-4 w-4" />
            <span>Last run: {lastRun}</span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="batch" className="text-sm font-medium text-slate-700">
                YC Batch (e.g. Spring 2025)
              </Label>
              <Input
                id="batch"
                value={batch}
                onChange={(e) => setBatch(e.target.value)}
                placeholder="Spring 2025"
                className="mt-2"
              />
            </div>

            <div>
              <Label htmlFor="mode" className="text-sm font-medium text-slate-700">
                Mode
              </Label>
              <Select value={mode} onValueChange={setMode}>
                <SelectTrigger className="mt-2">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="full">Full Scrape</SelectItem>
                  <SelectItem value="update">Update Only</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-end">
              <Button 
                type="submit" 
                className="w-full bg-primary hover:bg-blue-700"
                disabled={startScrapeMutation.isPending}
              >
                <Play className="h-4 w-4 mr-2" />
                {startScrapeMutation.isPending ? "Starting..." : "Start Scraping"}
              </Button>
            </div>
          </div>


        </form>
      </CardContent>
    </Card>
  );
}
