import { useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { PublicRoute } from '@/components/PublicRoute'
import { Login } from '@/features/auth/Login'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { useAuthStore } from '@/store/authStore'

const Dashboard = () => (
  <div className="rounded-lg border bg-card p-8 shadow-sm" dir="rtl">
    <h1 className="text-2xl font-bold">داشبورد (به زودی در روز پنجم...)</h1>
  </div>
)
const NotFound = () => <div className="p-8 text-red-500 font-bold" dir="rtl">404 - صفحه پیدا نشد</div>

function App() {
  const checkAuth = useAuthStore((state) => state.checkAuth)
  const isInitialized = useAuthStore((state) => state.isInitialized)

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  if (!isInitialized) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50" dir="rtl">
        <p className="text-lg font-medium text-muted-foreground animate-pulse">در حال بارگذاری سیستم...</p>
      </div>
    )
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<PublicRoute />}>
          <Route path="/login" element={<Login />} />
        </Route>

        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            <Route path="/" element={<Dashboard />} />
          </Route>
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App