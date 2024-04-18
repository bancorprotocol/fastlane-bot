from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Event:
    args: Dict[str, Any]
    event: str
    log_index: int
    transaction_index: int
    transaction_hash: str
    address: str
    block_hash: str
    block_number: int
    