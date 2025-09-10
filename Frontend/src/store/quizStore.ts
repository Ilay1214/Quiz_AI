import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { QuizSession, QuizQuestion } from '@/lib/api';

export interface UserAnswer {
  questionId: string;
  answers: string[];
}

export interface QuizState {
  // Session data
  session: QuizSession | null;
  currentQuestionIndex: number;
  
  // User data
  answers: UserAnswer[];
  flaggedQuestions: Set<string>;
  
  // Timer (for exam mode)
  timeRemaining: number; // seconds
  isTimerRunning: boolean;
  
  // UI state
  isSubmitted: boolean;
  
  // Actions
  setSession: (session: QuizSession) => void;
  setCurrentQuestion: (index: number) => void;
  setAnswer: (questionId: string, answers: string[]) => void;
  toggleFlag: (questionId: string) => void;
  startTimer: () => void;
  stopTimer: () => void;
  updateTimer: (seconds: number) => void;
  submitQuiz: () => void;
  resetQuiz: () => void;
  
  // Helper getters
  getCurrentQuestion: () => QuizQuestion | null;
  getAnswer: (questionId: string) => string[] | null;
  isQuestionAnswered: (questionId: string) => boolean;
  isQuestionFlagged: (questionId: string) => boolean;
  getProgress: () => { answered: number; total: number; flagged: number };
}

export const useQuizStore = create<QuizState>()(
  persist(
    (set, get) => ({
      session: null,
      currentQuestionIndex: 0,
      answers: [],
      flaggedQuestions: new Set(),
      timeRemaining: 0,
      isTimerRunning: false,
      isSubmitted: false,
      
      setSession: (session) => set({ 
        session, 
        timeRemaining: session.mode === 'exam' && session.duration 
          ? session.duration * 60 
          : 0,
        answers: [],
        flaggedQuestions: new Set(),
        currentQuestionIndex: 0,
        isSubmitted: false
      }),
      
      setCurrentQuestion: (index) => set({ currentQuestionIndex: index }),
      
      setAnswer: (questionId, answers) => set((state) => ({
        answers: state.answers.filter(a => a.questionId !== questionId).concat({
          questionId,
          answers
        })
      })),
      
      toggleFlag: (questionId) => set((state) => {
        const newFlagged = new Set(state.flaggedQuestions);
        if (newFlagged.has(questionId)) {
          newFlagged.delete(questionId);
        } else {
          newFlagged.add(questionId);
        }
        return { flaggedQuestions: newFlagged };
      }),
      
      startTimer: () => set({ isTimerRunning: true }),
      stopTimer: () => set({ isTimerRunning: false }),
      updateTimer: (seconds) => set({ timeRemaining: seconds }),
      
      submitQuiz: () => {
        set({ isSubmitted: true, isTimerRunning: false });
      },
      
      resetQuiz: () => set({
        session: null,
        currentQuestionIndex: 0,
        answers: [],
        flaggedQuestions: new Set(),
        timeRemaining: 0,
        isTimerRunning: false,
        isSubmitted: false,
      }),
      
      getCurrentQuestion: () => {
        const state = get();
        if (!state.session || state.currentQuestionIndex >= state.session.questions.length) {
          return null;
        }
        return state.session.questions[state.currentQuestionIndex];
      },
      
      getAnswer: (questionId) => {
        const answer = get().answers.find(a => a.questionId === questionId);
        return answer?.answers || null;
      },
      
      isQuestionAnswered: (questionId) => {
        const isAnswered = get().answers.some(a => a.questionId === questionId && a.answers.length > 0);
        return isAnswered;
      },
      
      isQuestionFlagged: (questionId) => {
        return get().flaggedQuestions.has(questionId);
      },
      
      getProgress: () => {
        const state = get();
        const total = state.session?.questions.length || 0;
        const answered = state.answers.filter(a => a.answers.length > 0).length;
        const flagged = state.flaggedQuestions.size;
        return { answered, total, flagged };
      }
    }),
    {
      name: 'quiz-storage',
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        session: state.session,
        currentQuestionIndex: state.currentQuestionIndex,
        answers: state.answers,
        flaggedQuestions: Array.from(state.flaggedQuestions),
        timeRemaining: state.timeRemaining,
        isSubmitted: state.isSubmitted,
      }),
      merge: (persistedState: any, currentState) => ({
        ...currentState,
        ...persistedState,
        flaggedQuestions: new Set(persistedState?.flaggedQuestions || []),
      }),
    }
  )
);