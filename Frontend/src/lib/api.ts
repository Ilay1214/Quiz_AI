const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export interface QuizQuestion {
  id: string;
  question: string;
  type: 'single' | 'multiple' | 'text';
  options?: string[];
  correctAnswers: string[];
  explanation?: string;
}

export interface QuizSession {
  id: string;
  questions: QuizQuestion[];
  mode: 'exam' | 'practice';
  duration?: number; // minutes for exam mode
  startTime: string;
}

export interface GenerateQuestionsRequest {
  file: File;
  numQuestions: number;
  duration?: number;
  mode: 'exam' | 'practice';
}

export interface GenerateQuestionsResponse {
  jobId: string;
}

export interface JobStatusResponse {
  status: 'pending' | 'processing' | 'completed' | 'failed';
  session?: QuizSession;
  error?: string;
}

export const api = {
  async generateQuestions(data: GenerateQuestionsRequest): Promise<GenerateQuestionsResponse> {
    const formData = new FormData();
    formData.append('file', data.file);
    formData.append('numQuestions', data.numQuestions.toString());
    if (data.duration) {
      formData.append('duration', data.duration.toString());
    }
    formData.append('mode', data.mode);

    const response = await fetch(`${API_BASE}/api/generate-questions`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  async getJobStatus(jobId: string): Promise<JobStatusResponse> {
    const response = await fetch(`${API_BASE}/api/job-status/${jobId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },
};