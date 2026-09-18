import os

from server.tools.order_tools import (
    get_order,
    search_orders,
    refund_order,
)


os.environ["AUTHENTICATED_CUSTOMER_ID"] = "CUS-101"


def test_get_own_order():

    result = get_order("ORD-1001")

    assert result["success"] is True
    assert result["order"]["order_id"] == "ORD-1001"


def test_get_other_customer_order():

    result = get_order("ORD-1002")

    assert result["success"] is False
    assert result["error_type"] == "authorization"


def test_unknown_order():

    result = get_order("ORD-9999")

    assert result["success"] is False
    assert result["error_type"] == "not_found"


def test_search_orders_only_returns_authenticated_customer():

    results = search_orders()

    assert len(results) == 2

    assert all(
        order["customer_id"] == "CUS-101"
        for order in results
    )