from dataclasses import dataclass, field

from app.models.sales import Sale


@dataclass
class CleaningReport:
    total_rows: int = 0
    cleaned_rows: int = 0
    duplicate_rows: int = 0
    invalid_rows: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass
class ImportReport(CleaningReport):
    imported_rows: int = 0


@dataclass
class ImportResult:
    rows: list[Sale] = field(default_factory=list)
    report: ImportReport = field(default_factory=ImportReport)
