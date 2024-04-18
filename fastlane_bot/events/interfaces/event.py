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

    @classmethod
    def from_dict(cls, data):
        return cls(
            args=data["args"],
            event=data["event"],
            log_index=data["logIndex"],
            transaction_index=data["transactionIndex"],
            transaction_hash=data["transactionHash"],
            address=data["address"],
            block_hash=data["blockHash"],
            block_number=data["blockNumber"],
        )
