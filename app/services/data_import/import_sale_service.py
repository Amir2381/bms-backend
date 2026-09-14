from sqlalchemy.orm import Session

from app.models.sales import Sale, SaleItem
from app.models.user import User
from app.repositories import product_repository, user_repository
from app.services.data_import.exceptions import (
    ImportedProductNotFoundError,
    ImportedSellerNotFoundError,
)
from app.services.data_import.types import ImportedSaleInput


class ImportSaleService:
    def create_sale(
        self,
        db: Session,
        sale_input: ImportedSaleInput,
        current_user: User,
    ) -> Sale:
        product = product_repository.get_product_by_name(
            db,
            sale_input.product,
        )

        if product is None:
            raise ImportedProductNotFoundError(
                f"Product {sale_input.product!r} not found."
            )

        if sale_input.seller:
            seller = user_repository.get_user_by_email(
                db,
                sale_input.seller,
            )

            if seller is None:
                raise ImportedSellerNotFoundError(
                    f"Seller {sale_input.seller!r} not found."
                )

            user_id = seller.id
        else:
            user_id = current_user.id

        sale_item = SaleItem(
            product_id=product.id,
            quantity=sale_input.quantity,
            unit_price=sale_input.unit_price,
        )

        sale = Sale(
            user_id=user_id,
            sale_date=sale_input.sale_date,
            items=[sale_item],
        )

        db.add(sale)
        db.flush()

        return sale

    def create_sales(
        self,
        db: Session,
        sale_inputs: list[ImportedSaleInput],
        current_user: User,
    ) -> list[Sale]:
        sales = []

        try:
            for sale_input in sale_inputs:
                sale = self.create_sale(
                    db=db,
                    sale_input=sale_input,
                    current_user=current_user,
                )
                sales.append(sale)

            db.commit()

        except Exception:
            db.rollback()
            raise

        return sales
