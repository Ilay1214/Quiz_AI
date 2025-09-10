import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { LoginResponse } from '@/lib/api';

interface AuthState {
  currentUser: Omit<LoginResponse, 'message'> | null;
  login: (userData: Omit<LoginResponse, 'message'>) => void;
  logout: () => void;
  clearAuth: () => void; // Added for explicit clearing, if needed
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      currentUser: null,
      login: (userData) => set({ currentUser: userData }),
      logout: () => set({ currentUser: null }),
      clearAuth: () => set({ currentUser: null }), // Can be same as logout
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage), // Using localStorage for auth
      onRehydrateStorage: (state) => {
        console.log('rehydration started', state);
        return (state, error) => {
          if (error) {
            console.log('an error happened during rehydration', error);
          } else {
            console.log('rehydration finished', state);
          }
        };
      },
      onNodeDestroyed: () => console.log('Node destroyed'),
    }
  )
);
