from typing import Any, Iterable, Iterator

from app.services.reporting.strategy import ReportStrategy


class ReportGenerator:
    def __init__(self, strategy: ReportStrategy) -> None:
        self._strategy = strategy

    def set_strategy(self, strategy: ReportStrategy) -> None:
        self._strategy = strategy

    def generate(
        self,
        headers: list[str],
        data: Iterable[dict[str, Any]],
    ) -> Iterator[str | bytes]:
        return self._strategy.generate(headers, data)
