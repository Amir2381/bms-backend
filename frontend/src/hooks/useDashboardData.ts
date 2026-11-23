import { useQuery } from '@tanstack/react-query'
import api from '@/services/api'
import { DashboardData } from '@/types/dashboard'

export const useDashboardData = () => {
    return useQuery<DashboardData>({
        queryKey: ['dashboard'],
        queryFn: async () => {
            const response = await api.get('/analytics/dashboard')
            return response.data
        },
    })
}