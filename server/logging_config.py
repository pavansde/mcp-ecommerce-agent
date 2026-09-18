import logging
from pathlib import Path


LOG_FILE = (
    Path(__file__).resolve().parents[1]
    / "logs"
    / "agent.log"
)

LOG_FILE.parent.mkdir(exist_ok=True)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
    ],
)


logger = logging.getLogger("ecommerce-agent")