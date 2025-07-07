from enum import Enum

class Currency(str, Enum):
    ARS = "ARS"  # Argentine Peso
    USD = "USD"  # US Dollar
    BTC = "BTC"  # Bitcoin
    ETH = "ETH"  # Ethereum

    @classmethod
    def valid_currencies(cls):
        return list(cls)

__all__ = [
    'Currency'
]