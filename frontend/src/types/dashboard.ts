export interface SummaryMetrics {
    total_sales: number
    total_profit: number
    profit_margin: number
    total_transactions: number
    average_order_value: number
    highest_sale: number | null
    lowest_sale: number | null
    average_daily_sales: number
    sold_products_count: number
    average_clv: number
}

export interface SalesTrendItem {
    date: string
    revenue: number
    transaction_count: number
}

export interface ProductPerformanceItem {
    product_id: number
    product_name: string
    quantity_sold: number
    revenue: number
    revenue_share: number
}

export interface DashboardData {
    metrics: SummaryMetrics
    trends: { trends: SalesTrendItem[] }
    top_products: { products: ProductPerformanceItem[] }
}