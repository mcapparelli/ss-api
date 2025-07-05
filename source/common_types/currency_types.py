from enum import Enum

class Currency(str, Enum):
    ARS = "ARS"  # Argentine Peso
    USD = "USD"  # US Dollar
    BTC = "BTC"  # Bitcoin
    ETH = "ETH"  # Ethereum

__all__ = [
    'Currency'
]