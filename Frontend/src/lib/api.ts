const API_BASE = import.meta.env.VITE_API_BASE || '';
const API_BASE = (import.meta.env.VITE_API_BASE && import.meta.env.VITE_API_BASE.trim() !== '') ? import.meta.env.VITE_API_BASE : '';

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
  userId: number; // Added for saving quizzes
  quizTitle: string; // Added for saving quizzes
}

export interface GenerateQuestionsResponse {
  jobId: string;
  quizId?: number; // Added for saved quizzes
}

export interface JobStatusResponse {
  status: 'pending' | 'processing' | 'completed' | 'failed';
  session?: QuizSession;
  error?: string;
  quizId?: number; // Added for saved quizzes
}

export interface SavedQuiz {
  quiz_id: number;
  user_id: number;
  title: string;
  quiz_data: QuizSession; // The full quiz session object
  mode: 'exam' | 'practice';
  duration?: number;
  created_at: string;
}

export interface AuthRequest {
  mail: string;
  password: string;
}

export interface RegisterResponse {
  message: string;
}

export interface LoginResponse {
  message: string;
  user_id: number;
  mail: string;
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
    formData.append('userId', data.userId.toString()); // Append userId
    formData.append('quizTitle', data.quizTitle); // Append quizTitle

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

  async register(data: AuthRequest): Promise<RegisterResponse> {
    const response = await fetch(`${API_BASE}/api/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  async login(data: AuthRequest): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE}/api/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  async fetchUserQuizzes(userId: number): Promise<SavedQuiz[]> {
    const response = await fetch(`${API_BASE}/api/quizzes/user/${userId}`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }
    return response.json();
  },

  async fetchQuizById(quizId: number): Promise<SavedQuiz> {
    const response = await fetch(`${API_BASE}/api/quizzes/${quizId}`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }
    return response.json();
  },
};