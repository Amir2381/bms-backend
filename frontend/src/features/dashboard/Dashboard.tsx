import { useDashboardData } from '@/hooks/useDashboardData'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { DollarSign, ShoppingCart, Activity, TrendingUp } from 'lucide-react'
import { SalesChart } from './SalesChart'
import { TopProductsChart } from './TopProductsChart'

export const Dashboard = () => {
    const { data, isLoading, isError } = useDashboardData()

    if (isError) {
        return (
            <div className="flex h-64 items-center justify-center rounded-lg border border-red-200 bg-red-50 text-red-600">
                خطا در دریافت اطلاعات داشبورد. لطفاً ارتباط با سرور را بررسی کنید.
            </div>
        )
    }

    if (isLoading || !data) {
        return (
            <div className="space-y-6">
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                    {[...Array(4)].map((_, i) => (
                        <Card key={i}>
                            <CardHeader className="flex flex-row items-center justify-between pb-2">
                                <Skeleton className="h-4 w-1/2" />
                                <Skeleton className="h-4 w-4 rounded-full" />
                            </CardHeader>
                            <CardContent>
                                <Skeleton className="h-8 w-3/4 mb-1" />
                                <Skeleton className="h-3 w-1/4" />
                            </CardContent>
                        </Card>
                    ))}
                </div>
                <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-4">
                    <Skeleton className="h-[380px] w-full rounded-xl col-span-1 lg:col-span-2" />
                    <Skeleton className="h-[380px] w-full rounded-xl col-span-1 lg:col-span-2" />
                </div>
            </div>
        )
    }

    const { metrics, trends, top_products } = data

    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-bold tracking-tight text-slate-900">داشبورد خلاصه عملکرد</h2>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="shadow-sm">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">فروش کل</CardTitle>
                        <DollarSign className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{metrics.total_sales.toLocaleString()} $</div>
                    </CardContent>
                </Card>
                <Card className="shadow-sm">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">سود خالص</CardTitle>
                        <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-green-600">{metrics.total_profit.toLocaleString()} $</div>
                        <p className="text-xs text-muted-foreground mt-1">
                            حاشیه سود: {metrics.profit_margin}%
                        </p>
                    </CardContent>
                </Card>
                <Card className="shadow-sm">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">تعداد تراکنش‌ها</CardTitle>
                        <ShoppingCart className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{metrics.total_transactions}</div>
                    </CardContent>
                </Card>
                <Card className="shadow-sm">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">ارزش میانگین سفارش</CardTitle>
                        <Activity className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{metrics.average_order_value.toLocaleString()} $</div>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-4">
                <SalesChart data={trends.trends} />
                <TopProductsChart data={top_products.products} />
            </div>
        </div>
    )
}