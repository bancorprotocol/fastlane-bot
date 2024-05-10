from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Event:
    args: Dict[str, Any]
    event: str
    log_index: Optional[int]
    transaction_index: Optional[int]
    transaction_hash: Optional[str]
    address: Optional[str]
    block_hash: Optional[str]
    block_number: Optional[int]

    @classmethod
    def from_dict(cls, data):
        return cls(
            args=data["args"],
            event=data["event"],
            log_index=data.get("logIndex", None),
            transaction_index=data.get("transactionIndex", None),
            transaction_hash=data.get("transactionHash", None),
            address=data.get("address", None),
            block_hash=data.get("blockHash", None),
            block_number=data.get("blockNumber", None),
        )
