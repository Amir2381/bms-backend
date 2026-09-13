from dataclasses import dataclass, field


@dataclass
class CleaningReport:
    total_rows: int = 0
    cleaned_rows: int = 0
    duplicate_rows: int = 0
    invalid_rows: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass
class ImportResult:
    rows: list[dict] = field(default_factory=list)
    report: CleaningReport = field(default_factory=CleaningReport)
