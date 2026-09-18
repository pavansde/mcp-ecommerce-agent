from server.auth import (
    authorize_customer,
    get_authenticated_customer_id,
)
from server.repositories.customer_repository import find_customer
from server.repositories.ticket_repository import create_ticket


def get_customer(customer_id: str) -> dict:
    """Get customer details for the authenticated customer."""

    try:
        authorize_customer(customer_id)
    except PermissionError:
        return {
            "success": False,
            "error_type": "authorization",
            "message": (
                "You are not authorized to access "
                "this customer's data."
            ),
        }

    customer = find_customer(customer_id)

    if customer is None:
        return {
            "success": False,
            "error_type": "not_found",
            "message": f"Customer {customer_id} not found.",
        }

    return {
        "success": True,
        "customer": customer,
    }


def create_support_ticket(
    customer_id: str,
    issue: str,
) -> dict:
    """Create a support ticket for the authenticated customer."""

    try:
        authorize_customer(customer_id)
    except PermissionError:
        return {
            "success": False,
            "error_type": "authorization",
            "message": (
                "You are not authorized to create "
                "a ticket for this customer."
            ),
        }

    customer = find_customer(customer_id)

    if customer is None:
        return {
            "success": False,
            "error_type": "not_found",
            "message": f"Customer {customer_id} not found.",
        }

    ticket = create_ticket(
        customer_id,
        issue,
    )

    return {
        "success": True,
        "ticket": ticket,
    }