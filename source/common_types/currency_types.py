from enum import Enum

class CurrencyType(str, Enum):
    ARS = "ARS"
    USD = "USD"
    BTC = "BTC"
    ETH = "ETH"

    FIAT_CURRENCIES = {ARS, USD}
    CRYPTO_CURRENCIES = {BTC, ETH}

    def is_fiat(self):
        return self in self.FIAT_CURRENCIES

    def is_crypto(self):
        return self in self.CRYPTO_CURRENCIES


    @classmethod
    def valid_currencies(cls):
        return list(cls)

__all__ = [
    'CurrencyType'
]