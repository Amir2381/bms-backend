import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { PublicRoute } from '@/components/PublicRoute'

const Login = () => <div className="flex items-center justify-center h-screen">Login Page (Coming Soon)</div>
const Dashboard = () => <div className="p-8">Dashboard (Coming Soon)</div>
const NotFound = () => <div className="p-8 text-red-500">404 - Not Found</div>

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<PublicRoute />}>
          <Route path="/login" element={<Login />} />
        </Route>

        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Dashboard />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App