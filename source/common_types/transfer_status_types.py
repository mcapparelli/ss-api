from enum import Enum

class TransferStatusType(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"

    @classmethod
    def valid_currencies(cls):
        return list(cls)

__all__ = [
    'TransferStatusType'
]