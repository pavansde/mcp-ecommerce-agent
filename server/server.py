import json
from mcp.server.mcpserver import MCPServer
from pathlib import Path

mcp = MCPServer("Order Service")

@mcp.resource("policy://refund")
def refund_policy() -> str:
    "company refund policy"
    return Path("refund_policy.md").read_text()

def load_orders():
    with open("orders.json", 'r') as file:
        return json.load(file)

@mcp.tool()
def get_order(order_id: str) -> dict:
    "Get order details by order id"
    orders = load_orders()

    for order in orders:
        if order["order_id"] == order_id:
            return order

    return {"error": f"Order {order_id} not found"}

@mcp.tool()
def search_order(customer_id: str) -> list[dict]:
    "Find all orders belong to a customer"
    orders = load_orders()

    return [
        order for order in orders if order['customer_id'] == customer_id
    ]


if __name__ == "__main__":
    mcp.run()
