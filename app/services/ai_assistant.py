import json
from typing import Any

from openai import OpenAI

from app.core.config import settings
from app.services.analytics.types import SalesTrend, SummaryMetrics


class AIAssistantService:
    def __init__(self) -> None:
        self.api_key = settings.ai_api_key
        self.client = (
            OpenAI(
                api_key=self.api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            )
            if self.api_key
            else None
        )

    def generate_insights(self, metrics: SummaryMetrics, trends: SalesTrend) -> str:
        if not self.client:
            return "⚠️ **AI API Key is not configured.** Please set `AI_API_KEY` in your `.env` file to enable AI insights."

        metrics_data = {
            "total_sales": str(metrics.total_sales),
            "total_profit": str(metrics.total_profit),
            "profit_margin": f"{metrics.profit_margin}%",
            "total_transactions": metrics.total_transactions,
            "average_order_value": str(metrics.average_order_value),
        }

        trends_data = [
            {"date": str(p.period), "revenue": str(p.revenue)}
            for p in trends.points[-14:]
        ]

        context = json.dumps(
            {"current_month_metrics": metrics_data, "recent_daily_trends": trends_data}
        )

        prompt = (
            "System Instructions: You are a highly analytical AI CFO assistant and an expert Business Analyst. "
            "Analyze the following recent sales performance data and metrics for our retail business.\n\n"
            f"Data Context:\n{context}\n\n"
            "Your task is to provide actionable business insights based ONLY on the provided data.\n"
            "Respond in Persian.\n"
            "Structure your response STRICTLY in Markdown with the following sections:\n\n"
            "### ۱. تفسیر عملکرد (Performance Interpretation)\n"
            "[وضعیت فعلی درآمد، حاشیه سود و الگوهای تراکنش را بررسی کن]\n\n"
            "### ۲. نقاط قوت و ضعف (Strengths & Weaknesses)\n"
            "[مشخص کن چه چیزی خوب کار می‌کند و چه بخشی نیاز به بهبود دارد]\n\n"
            "### ۳. پیشنهادات عملیاتی (Actionable Recommendations)\n"
            "[دقیقاً ۳ پیشنهاد استراتژیک یا عملیاتی بر اساس این اعداد ارائه بده]"
        )

        try:
            response = self.client.chat.completions.create(
                model="gemini-1.5-flash-latest",
                messages=[
                    {"role": "user", "content": prompt},
                ],
                max_tokens=800,
                temperature=0.7,
            )
            return response.choices[0].message.content or "هیچ بینشی تولید نشد."
        except Exception as e:
            return f"⚠️ **Error generating AI insights:**\n\n```text\n{str(e)}\n```"

    def chat_with_data(self, user_query: str, context_data: dict[str, Any]) -> str:
        if not self.client:
            return "سیستم هوش مصنوعی فعال نیست. لطفاً API Key را در تنظیمات وارد کنید."

        def default_serializer(obj):
            return str(obj)

        context_json = json.dumps(
            context_data, default=default_serializer, ensure_ascii=False
        )

        prompt = (
            "System Instructions: You are a direct, numbers-driven business data assistant. "
            "Answer the user's question accurately and concisely based ONLY on the provided Business Context JSON. "
            "If the answer cannot be found in the context, politely state that you don't have enough data to answer that specific question. "
            "Do not hallucinate or guess numbers.\n"
            "Respond entirely in conversational Persian.\n\n"
            f"--- Business Context ---\n{context_json}\n\n"
            f"--- User Question ---\n{user_query}"
        )

        try:
            response = self.client.chat.completions.create(
                model="gemini-1.5-flash-latest",
                messages=[
                    {"role": "user", "content": prompt},
                ],
                max_tokens=600,
                temperature=0.2,
            )
            return response.choices[0].message.content or "پاسخی دریافت نشد."
        except Exception as e:
            return f"خطا در پردازش هوش مصنوعی: {str(e)}"
