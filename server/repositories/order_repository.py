import json
from pathlib import Path


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "orders.json"
)


def load_orders(data_file: Path = DATA_FILE) -> list[dict]:
    with open(data_file, "r") as file:
        return json.load(file)


def save_orders(
    orders: list[dict],
    data_file: Path = DATA_FILE,
) -> None:
    with open(data_file, "w") as file:
        json.dump(orders, file, indent=2)


def find_order(
    order_id: str,
    data_file: Path = DATA_FILE,
) -> dict | None:

    orders = load_orders(data_file)

    for order in orders:
        if order["order_id"] == order_id:
            return order

    return None


def find_orders_by_customer(
    customer_id: str,
    data_file: Path = DATA_FILE,
) -> list[dict]:

    orders = load_orders(data_file)

    return [
        order
        for order in orders
        if order["customer_id"] == customer_id
    ]


def update_order(
    order_id: str,
    updates: dict,
    data_file: Path = DATA_FILE,
) -> dict | None:

    orders = load_orders(data_file)

    for order in orders:
        if order["order_id"] == order_id:
            order.update(updates)
            save_orders(orders, data_file)
            return order

    return None