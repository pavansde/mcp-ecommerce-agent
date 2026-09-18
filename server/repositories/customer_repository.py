import json
from pathlib import Path


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "customers.json"
)


def load_customers(
    data_file: Path = DATA_FILE,
) -> list[dict]:

    with open(data_file, "r") as file:
        return json.load(file)


def find_customer(
    customer_id: str,
    data_file: Path = DATA_FILE,
) -> dict | None:

    customers = load_customers(data_file)

    for customer in customers:
        if customer["customer_id"] == customer_id:
            return customer

    return None