import { create } from 'zustand'
import api from '@/services/api'

export interface User {
    id: number
    full_name: string
    email: string
    role: string
    branch_id: number
}

interface AuthState {
    user: User | null
    isInitialized: boolean
    setUser: (user: User | null) => void
    logout: () => void
    checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
    user: null,
    isInitialized: false,
    setUser: (user) => set({ user }),
    logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        set({ user: null })
    },
    checkAuth: async () => {
        try {
            if (localStorage.getItem('access_token')) {
                const response = await api.get('/auth/me')
                set({ user: response.data, isInitialized: true })
            } else {
                set({ isInitialized: true })
            }
        } catch (error) {
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            set({ user: null, isInitialized: true })
        }
    },
}))