from enum import Enum

class CurrencyType(str, Enum):
    ARS = "ARS"
    USD = "USD"
    BTC = "BTC"
    ETH = "ETH"

    def is_fiat(self):
        return self in {CurrencyType.ARS, CurrencyType.USD}

    def is_crypto(self):
        return self in {CurrencyType.BTC, CurrencyType.ETH}

    @classmethod
    def valid_currencies(cls):
        return list(cls)

__all__ = [
    'CurrencyType'
]