from sqlalchemy.orm import Session

from app.models.user import User
from app.services.data_import.cleaner import DataCleaner
from app.services.data_import.domain_mapper import DomainMapper
from app.services.data_import.import_sale_service import ImportSaleService
from app.services.data_import.mapper import ColumnMapper
from app.services.data_import.parser import FileParser
from app.services.data_import.report import CleaningReport, ImportResult
from app.services.data_import.validator import ImportValidator


class ImportService:
    def __init__(
        self,
        parser: FileParser,
        validator: ImportValidator,
        mapper: ColumnMapper,
        cleaner: DataCleaner,
        domain_mapper: DomainMapper,
        sale_service: ImportSaleService,
    ):
        self.parser = parser
        self.validator = validator
        self.mapper = mapper
        self.cleaner = cleaner
        self.domain_mapper = domain_mapper
        self.sale_service = sale_service

    def process(
        self,
        file_path: str,
        db: Session,
        current_user: User,
    ) -> ImportResult:
        parsed_data = self.parser.parse(file_path)

        self.validator.validate(parsed_data.headers)

        mapped_rows = self.mapper.map(parsed_data.rows)

        report = CleaningReport()

        cleaned_rows = self.cleaner.clean(
            mapped_rows,
            report,
        )

        sale_inputs = self.domain_mapper.map(cleaned_rows)

        sales = self.sale_service.create_sales(
            db=db,
            sale_inputs=sale_inputs,
            current_user=current_user,
        )

        return ImportResult(
            rows=sales,
            report=report,
        )
