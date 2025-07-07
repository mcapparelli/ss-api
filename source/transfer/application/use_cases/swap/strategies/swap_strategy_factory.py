from source.transfer.application.use_cases.swap.strategies.crypto_to_crypto import CryptoToCryptoStrategy
from source.transfer.application.use_cases.swap.strategies.crypto_to_fiat import CryptoToFiatStrategy
from source.transfer.application.use_cases.swap.swap_result import SwapResult
from .swap_interface import ISwap
from .fiat_to_fiat_strategy import FiatToFiatStrategy
from source.common_types.currency_types import CurrencyType

class SwapStrategyFactory:
    def create_strategy(self, from_currency: str, to_currency: str) -> ISwap:
        self._validate_currencies(from_currency, to_currency)
        
        from_is_fiat = CurrencyType(from_currency).is_fiat()
        to_is_fiat = CurrencyType(to_currency).is_fiat()
        
        if from_is_fiat and to_is_fiat:
            return FiatToFiatStrategy()
        elif not from_is_fiat and not to_is_fiat:
            return CryptoToCryptoStrategy()
        else:
            return CryptoToFiatStrategy()
    
    def _validate_currencies(self, from_currency: str, to_currency: str) -> None:
        valid_currencies = [currency.value for currency in CurrencyType]
        
        if from_currency not in valid_currencies:
            raise ValueError(f"Currency {from_currency} is not a supported currency")
        
        if to_currency not in valid_currencies:
            raise ValueError(f"Currency {to_currency} is not a supported currency")
    
        
    async def execute_swap(self, from_currency: str, to_currency: str, amount: float, balance) -> SwapResult:
        self._validate_currencies(from_currency, to_currency)
        strategy = self.create_strategy(from_currency, to_currency)
        return await strategy.execute_swap(from_currency, to_currency, amount, balance) 
    