import { useNavigate } from 'react-router-dom'
import { LogOut, User as UserIcon, Menu } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import api from '@/services/api'
import { Button } from '@/components/ui/button'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Sidebar } from './Sidebar'
import { toast } from 'sonner'

export const Topbar = () => {
    const user = useAuthStore((state) => state.user)
    const logout = useAuthStore((state) => state.logout)
    const navigate = useNavigate()

    const handleLogout = async () => {
        try {
            const refreshToken = localStorage.getItem('refresh_token')
            if (refreshToken) {
                await api.post('/auth/logout', { refresh_token: refreshToken })
            }
        } catch (error) {
            console.error('Logout failed on server', error)
        } finally {
            logout()
            toast.info('از سیستم خارج شدید')
            navigate('/login')
        }
    }

    return (
        <header className="flex h-16 items-center justify-between border-b bg-card px-6">
            <div className="flex items-center md:hidden">
                <Sheet>
                    <SheetTrigger asChild>
                        <Button variant="ghost" size="icon" className="md:hidden">
                            <Menu className="h-5 w-5" />
                        </Button>
                    </SheetTrigger>
                    <SheetContent side="right" className="w-64 p-0">
                        <Sidebar className="w-full border-none" />
                    </SheetContent>
                </Sheet>
            </div>

            <div className="hidden md:block"></div>

            <div className="flex items-center gap-4" dir="rtl">
                <div className="hidden text-left md:block">
                    <p className="text-sm font-medium leading-none">{user?.full_name}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                        {user?.role === 'ADMIN' ? 'مدیر سیستم' : 'فروشنده'} | شعبه {user?.branch_id}
                    </p>
                </div>
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                            <Avatar className="h-10 w-10">
                                <AvatarFallback className="bg-primary/10 text-primary">
                                    <UserIcon className="h-5 w-5" />
                                </AvatarFallback>
                            </Avatar>
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-56" align="end" forceMount dir="rtl">
                        <DropdownMenuLabel className="font-normal">
                            <div className="flex flex-col space-y-1">
                                <p className="text-sm font-medium leading-none">{user?.full_name}</p>
                                <p className="text-xs leading-none text-muted-foreground">
                                    {user?.email}
                                </p>
                            </div>
                        </DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem onClick={handleLogout} className="text-red-600 focus:text-red-600 focus:bg-red-50 cursor-pointer">
                            <LogOut className="mr-2 h-4 w-4 ml-2" />
                            <span>خروج از سیستم</span>
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>
        </header>
    )
}