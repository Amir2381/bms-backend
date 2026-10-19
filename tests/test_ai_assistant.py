from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.core.config import settings
from app.services.ai_assistant import AIAssistantService


def _create_mock_openai_response(text: str) -> MagicMock:
    mock_message = MagicMock()
    mock_message.content = text
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response


def test_ai_insights_endpoint_with_mocked_llm(client: TestClient, monkeypatch):
    monkeypatch.setattr(settings, "ai_api_key", "test-mock-key")
    expected_markdown = "### ۱. تفسیر عملکرد\nفروش رشد داشته است."

    with patch("app.services.ai_assistant.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = _create_mock_openai_response(
            expected_markdown
        )
        mock_openai_cls.return_value = mock_client

        response = client.get("/analytics/ai-insights")
        assert response.status_code == 200
        data = response.json()
        assert data["markdown_content"] == expected_markdown
        mock_client.chat.completions.create.assert_called_once()


def test_ai_chat_endpoint_with_mocked_llm_and_rag_context(
    client: TestClient, monkeypatch
):
    monkeypatch.setattr(settings, "ai_api_key", "test-mock-key")
    expected_answer = "پرفروش‌ترین محصول شما Test Product است."

    with patch("app.services.ai_assistant.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = _create_mock_openai_response(
            expected_answer
        )
        mock_openai_cls.return_value = mock_client

        response = client.post(
            "/analytics/ai-chat",
            json={"query": "کدام محصول و در کدام شعبه بیشترین فروش و سود را داشت؟"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == expected_answer

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        sent_prompt = call_kwargs["messages"][0]["content"]
        assert "top_products" in sent_prompt
        assert "branch_comparison" in sent_prompt
        assert "metrics_last_30_days" in sent_prompt


def test_ai_assistant_without_api_key(monkeypatch):
    monkeypatch.setattr(settings, "ai_api_key", None)
    service = AIAssistantService()

    chat_res = service.chat_with_data("سوال تستی", {"total_sales": 100})
    assert "سیستم هوش مصنوعی فعال نیست" in chat_res
