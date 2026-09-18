from mcp.server import MCPServer

from server.tools.order_tools import get_order, search_orders, refund_order
from server.resources.policy_resources import refund_policy
from server.tools.customer_tools import get_customer, create_support_ticket


mcp = MCPServer("Ecommerce Support Server")


@mcp.tool()
def get_order_tool(order_id: str) -> dict:
    """Get order details by order ID."""
    return get_order(order_id)


@mcp.tool()
def search_orders_tool() -> list[dict]:
    """Find all orders belonging to the authenticated customer."""
    return search_orders()

@mcp.tool()
def refund_order_tool(order_id: str) -> dict:
    """Request a refund for an order."""
    return refund_order(order_id)


@mcp.resource("policy://refund")
def refund_policy_resource() -> str:
    """Company refund policy."""
    return refund_policy()

@mcp.tool()
def get_customer_tool(customer_id: str) -> dict:
    """Get customer details by customer ID."""
    return get_customer(customer_id)


@mcp.tool()
def create_support_ticket_tool(
    customer_id: str,
    issue: str
) -> dict:
    """Create a support ticket for a customer issue."""
    return create_support_ticket(customer_id, issue)


if __name__ == "__main__":
    mcp.run()