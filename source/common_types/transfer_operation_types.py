from enum import Enum

class TransferOperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER = "TRANSFER"
    SWAP = "SWAP"
    PAYMENT = "PAYMENT"

    @classmethod
    def valid_currencies(cls):
        return list(cls)

__all__ = [
    'TransferOperationType'
]