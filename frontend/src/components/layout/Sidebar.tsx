import { NavLink } from 'react-router-dom'
import { LayoutDashboard, ShoppingCart, Users, Package } from 'lucide-react'
import { cn } from '@/utils'

const navItems = [
    { name: 'داشبورد', href: '/', icon: LayoutDashboard },
    { name: 'فروش‌ها', href: '/sales', icon: ShoppingCart },
    { name: 'محصولات', href: '/products', icon: Package },
    { name: 'مشتریان', href: '/customers', icon: Users },
]

export const Sidebar = ({ className }: { className?: string }) => {
    return (
        <aside className={cn("flex h-full w-64 flex-col border-l bg-card", className)}>
            <div className="flex h-16 items-center justify-center border-b px-6">
                <h2 className="text-lg font-bold tracking-tight text-primary">BMS System</h2>
            </div>
            <nav className="flex-1 space-y-1 p-4" dir="rtl">
                {navItems.map((item) => (
                    <NavLink
                        key={item.href}
                        to={item.href}
                        className={({ isActive }) =>
                            cn(
                                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                                isActive
                                    ? 'bg-primary/10 text-primary'
                                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                            )
                        }
                    >
                        <item.icon className="h-4 w-4" />
                        {item.name}
                    </NavLink>
                ))}
            </nav>
        </aside>
    )
}