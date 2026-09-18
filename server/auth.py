import os

from dotenv import load_dotenv


load_dotenv()


def get_authenticated_customer_id() -> str:
    customer_id = os.getenv("AUTHENTICATED_CUSTOMER_ID")

    if not customer_id:
        raise RuntimeError(
            "Authenticated customer context is missing."
        )

    return customer_id


def authorize_customer(customer_id: str):
    authenticated_customer = get_authenticated_customer_id()

    if customer_id != authenticated_customer:
        raise PermissionError(
            "You are not authorized to access this customer's data."
        )