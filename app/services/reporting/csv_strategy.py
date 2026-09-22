import csv
import io
from typing import Any, Iterable, Iterator


class CsvReportStrategy:
    def generate(
        self,
        headers: list[str],
        data: Iterable[dict[str, Any]],
    ) -> Iterator[str]:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)

        writer.writeheader()
        yield output.getvalue()
        output.truncate(0)
        output.seek(0)

        for row in data:
            writer.writerow(row)
            yield output.getvalue()
            output.truncate(0)
            output.seek(0)
