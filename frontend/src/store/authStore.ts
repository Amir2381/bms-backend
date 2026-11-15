import { create } from 'zustand'

export interface User {
    id: number
    full_name: string
    email: string
    role: string
    branch_id: number
}

interface AuthState {
    user: User | null
    setUser: (user: User | null) => void
    logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
    user: null,
    setUser: (user) => set({ user }),
    logout: () => set({ user: null }),
}))