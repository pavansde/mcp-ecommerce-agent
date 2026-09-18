import json

from server.repositories.order_repository import (
    find_order,
    find_orders_by_customer,
    update_order,
)


def create_test_orders(tmp_path):
    orders = [
        {
            "order_id": "TEST-1001",
            "customer_id": "CUS-101",
            "status": "shipped",
            "amount": 500,
            "refund_status": "not_requested",
        },
        {
            "order_id": "TEST-1002",
            "customer_id": "CUS-102",
            "status": "delivered",
            "amount": 800,
            "refund_status": "not_requested",
        },
    ]

    file_path = tmp_path / "orders.json"

    with open(file_path, "w") as file:
        json.dump(orders, file, indent=2)

    return file_path


def test_find_order(tmp_path):
    file_path = create_test_orders(tmp_path)

    order = find_order(
        "TEST-1001",
        file_path,
    )

    assert order is not None
    assert order["customer_id"] == "CUS-101"


def test_find_orders_by_customer(tmp_path):
    file_path = create_test_orders(tmp_path)

    orders = find_orders_by_customer(
        "CUS-101",
        file_path,
    )

    assert len(orders) == 1
    assert orders[0]["order_id"] == "TEST-1001"


def test_update_order(tmp_path):
    file_path = create_test_orders(tmp_path)

    updated = update_order(
        "TEST-1001",
        {"refund_status": "requested"},
        file_path,
    )

    assert updated["refund_status"] == "requested"

    order = find_order(
        "TEST-1001",
        file_path,
    )

    assert order["refund_status"] == "requested"