import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Topbar } from './Topbar'

export const DashboardLayout = () => {
    return (
        <div className="flex h-screen overflow-hidden bg-slate-50">
            <Sidebar className="hidden md:flex" />

            <div className="flex flex-1 flex-col overflow-hidden">
                <Topbar />
                <main className="flex-1 overflow-y-auto p-4 md:p-8" dir="rtl">
                    <Outlet />
                </main>
            </div>
        </div>
    )
}