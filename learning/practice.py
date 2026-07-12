# class Product:
#     def __init__(self, name: str, price: float):
#         self.name = name
#         self.price = price

#     def __str__(self) -> str:
#         return f"{self.name} - ${self.price}"

#     def __repr__(self) -> str:
#         return f"Product(name={self.name!r}, price={self.price})"

#     def __eq__(self, other: object) -> bool:
#         if not isinstance(other, Product):
#             return NotImplemented

#         return self.name == other.name and self.price == other.price


# p1 = Product("Laptop", 1200)
# p2 = Product("Laptop", 1200)

# print(p1)
# print(str(p1))
# print(p1 == "laptop")
# print([p1, p2])
# print(repr(p1))
# print(p1 == p2)


# class DatabaseSession:
#     def __enter__(self):
#         print("Connecting to database...")
#         return self

#     def __exit__(self, exc_type, exc_value, traceback):
#         print(exc_type)
#         print(exc_value)
#         print(traceback)
#         print("Closing database connection...")


# with DatabaseSession() as db:
#     print("Running query...")
#     10 / 0


# from typing import TypedDict, Protocol


# class ProductData(TypedDict):
#     name: str
#     price: float
#     stock: int


# class Printable(Protocol):
#     def print_info(self) -> None: ...


# class Product:
#     def print_info(self) -> None: ...


# def show(item: Printable) -> None:
#     item.print_info()


# product = Product()
# show(product)


# from itertools import chain

# products = ["Laptop", "Mouse"]
# phones = ["iPhone", "Samsung"]
# laptops = ["asus", "aser"]

# for item in chain(products, phones, laptops):
#     print(item)


# from itertools import count, islice

# numbers = count(1)

# print(list(islice(numbers, 10)))


# from itertools import product

# colors = ["Red", "Blue"]
# sizes = ["S", "M"]

# for item in product(colors, sizes):
#     print(item)
