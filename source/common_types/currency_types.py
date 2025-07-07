from enum import Enum

class CurrencyType(str, Enum):
    ARS = "ARS"  # Argentine Peso
    USD = "USD"  # US Dollar
    BTC = "BTC"  # Bitcoin
    ETH = "ETH"  # Ethereum

    @classmethod
    def valid_currencies(cls):
        return list(cls)

__all__ = [
    'CurrencyType'
]