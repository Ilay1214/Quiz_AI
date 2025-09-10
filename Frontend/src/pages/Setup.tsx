import { useState, useCallback, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useDropzone } from "react-dropzone";
import { useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { useQuizStore } from "@/store/quizStore";
import { useAuthStore } from "@/store/authStore";
import { Upload, FileText, Loader2 } from "lucide-react";
import Header from "@/components/common/Header";

const Setup = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { toast } = useToast();
  const setSession = useQuizStore((state) => state.setSession);
  const { currentUser, logout } = useAuthStore();

  // Removed useEffect for redirecting unauthenticated users

  const [mode, setMode] = useState<'exam' | 'practice'>(
    location.state?.mode || 'exam'
  );
  const [file, setFile] = useState<File | null>(null);
  const [numQuestions, setNumQuestions] = useState(10);
  const [duration, setDuration] = useState(30);
  const [jobId, setJobId] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
  });

  // Generate questions mutation
  const generateMutation = useMutation({
    mutationFn: api.generateQuestions,
    onSuccess: (data) => {
      setJobId(data.jobId);
      startPolling(data.jobId);
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Poll job status
  const pollMutation = useMutation({
    mutationFn: api.getJobStatus,
    onSuccess: (data) => {
      if (data.status === 'completed' && data.session) {
        setSession(data.session);
        navigate('/quiz');
      } else if (data.status === 'failed') {
        toast({
          title: "Generation Failed",
          description: data.error || "Failed to generate questions",
          variant: "destructive",
        });
        setJobId(null);
      } else if (data.status === 'processing' || data.status === 'pending') {
        // Continue polling
        setTimeout(() => {
          if (jobId) {
            pollMutation.mutate(jobId);
          }
        }, 2000);
      }
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
      setJobId(null);
    },
  });

  const startPolling = (id: string) => {
    pollMutation.mutate(id);
  };

  const handleGenerate = () => {
    if (!file) {
      toast({
        title: "File Required",
        description: "Please upload a file to generate questions.",
        variant: "destructive",
      });
      return;
    }

    if (numQuestions < 1 || numQuestions > 65) {
      toast({
        title: "Invalid Number of Questions",
        description: "Number of questions must be between 1 and 65.",
        variant: "destructive",
      });
      return;
    }

    if (mode === 'exam' && (duration < 1 || duration > 180)) {
      toast({
        title: "Invalid Duration",
        description: "Duration must be between 1 and 180 minutes.",
        variant: "destructive",
      });
      return;
    }

    generateMutation.mutate({
      file,
      numQuestions,
      duration: mode === 'exam' ? duration : undefined,
      mode,
    });
  };

  const handleReset = () => {
    setFile(null);
    setNumQuestions(10);
    setDuration(30);
    setJobId(null);
  };

  const isLoading = generateMutation.isPending || jobId !== null;

  return (
    <div className="min-h-screen bg-background py-8">
      <Header showBackButton={true} title="Quiz Setup" />
      <div className="container mx-auto px-4 max-w-2xl relative">
        <div className="mb-8 mt-8">
          <h1 className="text-3xl font-bold">Setup Your Quiz</h1>
          <p className="text-muted-foreground mt-2">
            Configure your quiz parameters and upload your study materials
          </p>
        </div>

        <div className="space-y-6">
          {/* Mode Selection */}
          <Card>
            <CardHeader>
              <CardTitle>Quiz Mode</CardTitle>
              <CardDescription>
                Choose between timed exam or practice mode
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-4">
                <Label htmlFor="mode-switch">Practice Mode</Label>
                <Switch
                  id="mode-switch"
                  checked={mode === 'exam'}
                  onCheckedChange={(checked) => setMode(checked ? 'exam' : 'practice')}
                />
                <Label htmlFor="mode-switch">Exam Mode</Label>
              </div>
              <p className="text-sm text-muted-foreground mt-2">
                {mode === 'exam' 
                  ? 'Timed quiz with results shown after completion' 
                  : 'Untimed quiz with immediate feedback on each question'
                }
              </p>
            </CardContent>
          </Card>

          {/* File Upload */}
          <Card>
            <CardHeader>
              <CardTitle>Upload Study Material</CardTitle>
              <CardDescription>
                Upload a PDF, DOCX, or TXT file with your study content
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? 'border-primary bg-primary/5'
                    : 'border-muted-foreground/25 hover:border-primary/50 hover:bg-primary/5'
                }`}
              >
                <input {...getInputProps()} />
                <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                {file ? (
                  <div className="space-y-2">
                    <div className="flex items-center justify-center gap-2">
                      <FileText className="w-5 h-5 text-primary" />
                      <span className="font-medium">{file.name}</span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        setFile(null);
                      }}
                    >
                      Remove File
                    </Button>
                  </div>
                ) : (
                  <div>
                    <p className="text-lg mb-2">
                      {isDragActive
                        ? 'Drop your file here'
                        : 'Drag & drop your file here, or click to browse'}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Supports PDF, DOCX, and TXT files
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Parameters */}
          <Card>
            <CardHeader>
              <CardTitle>Quiz Parameters</CardTitle>
              <CardDescription>
                Configure the number of questions and duration
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="num-questions">Number of Questions (1-65)</Label>
                <Input
                  id="num-questions"
                  type="number"
                  min="1"
                  max="65"
                  value={numQuestions}
                  onChange={(e) => setNumQuestions(parseInt(e.target.value) || 1)}
                  className="mt-1"
                />
              </div>

              {mode === 'exam' && (
                <div>
                  <Label htmlFor="duration">Duration (minutes)</Label>
                  <Input
                    id="duration"
                    type="number"
                    min="1"
                    max="180"
                    value={duration}
                    onChange={(e) => setDuration(parseInt(e.target.value) || 1)}
                    className="mt-1"
                  />
                  <p className="text-sm text-muted-foreground mt-1">
                    1-180 minutes. Maximum 3 hours.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex gap-4">
            <Button
              onClick={handleGenerate}
              disabled={!file || isLoading}
              className="flex-1"
              size="lg"
            >
              {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Generate Questions
            </Button>
            <Button
              variant="outline"
              onClick={handleReset}
              disabled={isLoading}
              size="lg"
            >
              Reset
            </Button>
          </div>

          {/* Status */}
          {isLoading && (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
                  <p className="font-medium">Processing your document...</p>
                  <p className="text-sm text-muted-foreground">
                    This may take a few minutes depending on file size
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default Setup;