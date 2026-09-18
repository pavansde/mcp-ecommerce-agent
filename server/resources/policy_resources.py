from pathlib import Path


POLICY_FILE = (
    Path(__file__).resolve().parents[2]
    / "policies"
    / "refund_policy.md"
)


def refund_policy() -> str:
    """Company refund policy."""

    return POLICY_FILE.read_text()