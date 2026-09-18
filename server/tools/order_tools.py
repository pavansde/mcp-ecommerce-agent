import json
from pathlib import Path

from server.auth import (
    authorize_customer,
    get_authenticated_customer_id,
)
from server.logging_config import logger
from server.repositories.order_repository import (
    find_order,
    find_orders_by_customer,
    update_order,
)


def get_order(order_id: str) -> dict:
    """Get an order belonging to the authenticated customer."""

    order = find_order(order_id)

    if order is None:
        logger.info(
            "ORDER_NOT_FOUND | order_id=%s",
            order_id,
        )

        return {
            "success": False,
            "error_type": "not_found",
            "message": f"Order {order_id} does not exist.",
        }

    authenticated_customer = get_authenticated_customer_id()

    if order["customer_id"] != authenticated_customer:
        logger.warning(
            "AUTHORIZATION_FAILED | order_id=%s",
            order_id,
        )

        return {
            "success": False,
            "error_type": "authorization",
            "message": (
                "Order exists but does not belong "
                "to the authenticated customer."
            ),
        }

    return {
        "success": True,
        "order": order,
    }


def search_orders() -> list[dict]:
    """Find all orders belonging to the authenticated customer."""

    customer_id = get_authenticated_customer_id()

    return find_orders_by_customer(customer_id)


def refund_order(order_id: str) -> dict:
    """Request a refund for an order belonging to the authenticated customer."""

    logger.info(
        "REFUND_REQUESTED | order_id=%s",
        order_id,
    )

    order = find_order(order_id)

    if order is None:
        return {
            "success": False,
            "error_type": "not_found",
            "message": f"Order {order_id} does not exist.",
        }

    authenticated_customer = get_authenticated_customer_id()

    if order["customer_id"] != authenticated_customer:
        logger.warning(
            "AUTHORIZATION_FAILED | refund_order=%s",
            order_id,
        )

        return {
            "success": False,
            "error_type": "authorization",
            "message": "You are not authorized to refund this order.",
        }

    if order["status"] == "cancelled":
        logger.info(
            "REFUND_REJECTED | order_id=%s | reason=cancelled",
            order_id,
        )

        return {
            "success": False,
            "error_type": "business_rule",
            "message": "Cancelled orders cannot be refunded.",
        }

    if order["refund_status"] == "requested":
        logger.info(
            "REFUND_REJECTED | order_id=%s | reason=duplicate",
            order_id,
        )

        return {
            "success": False,
            "error_type": "business_rule",
            "message": "Refund has already been requested.",
        }

    updated_order = update_order(
        order_id,
        {"refund_status": "requested"},
    )

    logger.info(
        "REFUND_SUCCESS | order_id=%s | amount=%s",
        order_id,
        updated_order["amount"],
    )

    return {
        "success": True,
        "order_id": order_id,
        "refund_status": "requested",
        "amount": updated_order["amount"],
        "message": "Refund request submitted successfully.",
    }