import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import api from '@/services/api'

export const Login = () => {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            const params = new URLSearchParams()
            params.append('username', email.trim())
            params.append('password', password)

            const response = await api.post('/auth/login', params, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            })

            localStorage.setItem('access_token', response.data.access_token)
            localStorage.setItem('refresh_token', response.data.refresh_token)

            navigate('/')
        } catch (err: any) {
            console.error("Login Error:", err)
            if (err.response) {
                const detail = err.response.data?.detail
                const message = typeof detail === 'string' ? detail : JSON.stringify(detail)
                setError(`خطای سرور (${err.response.status}): ${message || 'اطلاعات نامعتبر است'}`)
            } else if (err.request) {
                setError('خطای شبکه: سرور بک‌اند در دسترس نیست (Network Error)')
            } else {
                setError(`خطای نامشخص: ${err.message}`)
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="flex items-center justify-center min-h-screen bg-slate-50">
            <Card className="w-full max-w-md shadow-sm">
                <CardHeader className="space-y-1 text-center">
                    <CardTitle className="text-2xl font-bold tracking-tight">ورود به سیستم</CardTitle>
                    <CardDescription>
                        ایمیل و رمز عبور خود را برای دسترسی به داشبورد وارد کنید
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleLogin} className="space-y-4">
                        <div className="space-y-2 text-right" dir="rtl">
                            <Label htmlFor="email">ایمیل</Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="admin@example.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                className="text-left"
                                dir="ltr"
                            />
                        </div>
                        <div className="space-y-2 text-right" dir="rtl">
                            <Label htmlFor="password">رمز عبور</Label>
                            <Input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className="text-left"
                                dir="ltr"
                            />
                        </div>
                        {error && <div className="text-sm text-red-500 text-right font-medium">{error}</div>}
                        <Button type="submit" className="w-full" disabled={loading}>
                            {loading ? 'در حال ورود...' : 'ورود'}
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    )
}