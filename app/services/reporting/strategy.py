from typing import Any, Iterable, Iterator, Protocol


class ReportStrategy(Protocol):
    def generate(
        self,
        headers: list[str],
        data: Iterable[dict[str, Any]],
    ) -> Iterator[str | bytes]: ...
