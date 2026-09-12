class UserNotFoundError(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User {user_id} not found")


class ProductNotFoundError(Exception):
    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f"Product {product_id} not found")


class InsufficientStockError(Exception):
    def __init__(
        self,
        product_id: int,
        requested_quantity: int,
        available_quantity: int,
    ):
        self.product_id = product_id
        self.requested_quantity = requested_quantity
        self.available_quantity = available_quantity

        super().__init__(
            f"Not enough stock for product {product_id}: "
            f"requested {requested_quantity}, "
            f"available {available_quantity}"
        )
