import json
from pathlib import Path


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "tickets.json"
)


def load_tickets(
    data_file: Path = DATA_FILE,
) -> list[dict]:

    with open(data_file, "r") as file:
        return json.load(file)


def save_tickets(
    tickets: list[dict],
    data_file: Path = DATA_FILE,
) -> None:

    with open(data_file, "w") as file:
        json.dump(tickets, file, indent=2)


def create_ticket(
    customer_id: str,
    issue: str,
    data_file: Path = DATA_FILE,
) -> dict:

    tickets = load_tickets(data_file)

    ticket_id = f"TKT-{1001 + len(tickets)}"

    ticket = {
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "issue": issue,
        "status": "open",
    }

    tickets.append(ticket)

    save_tickets(tickets, data_file)

    return ticket