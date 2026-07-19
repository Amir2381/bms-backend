def calculate_total(price: float, quantity: int):
    return price * quantity


def test_calculate_total():
    assert calculate_total(100, 2) == 200
