from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.customer import Customer
from app.models.sales import Sale, SaleItem
from app.models.user import User
from app.models.audit_log import AuditLog
from app.repositories import (
    category_repository,
    customer_repository,
    product_repository,
    user_repository,
)
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

        if sale_input.category:
            category = category_repository.get_category_by_name(db, sale_input.category)
            if not category:
                category = Category(name=sale_input.category)
                db.add(category)
                db.flush()

            if product.category_id != category.id:
                product.category_id = category.id
                db.add(product)

        customer_id = None
        if sale_input.customer_phone:
            customer = customer_repository.get_customer_by_phone(
                db, sale_input.customer_phone
            )
            if not customer:
                customer = Customer(
                    phone=sale_input.customer_phone, full_name="Imported Customer"
                )
                db.add(customer)
                db.flush()
            customer_id = customer.id

        if sale_input.seller:
            seller = user_repository.get_user_by_email(
                db,
                sale_input.seller,
            )

            if seller is None:
                raise ImportedSellerNotFoundError(
                    f"Seller {sale_input.seller!r} not found."
                )

            target_user = seller
        else:
            target_user = current_user

        sale_item = SaleItem(
            product_id=product.id,
            quantity=sale_input.quantity,
            unit_price=sale_input.unit_price,
            cost_price=(
                sale_input.cost_price
                if sale_input.cost_price is not None
                else product.cost_price
            ),
        )

        sale = Sale(
            user_id=target_user.id,
            branch_id=target_user.branch_id,
            customer_id=customer_id,
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

            if sales:
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action="IMPORT_SALES",
                    entity_type="SaleBatch",
                    entity_id=None,
                    details={"imported_rows": len(sales)},
                )
                db.add(audit_log)
                db.commit()

        except Exception:
            db.rollback()
            raise

        return sales
