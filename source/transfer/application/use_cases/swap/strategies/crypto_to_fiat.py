from decimal import Decimal
from datetime import datetime
from source.common_types.currency_types import CurrencyType
from source.transfer.application.use_cases.swap.swap_result import SwapResult
from .swap_interface import ISwap
from source.user.domain.entities.user_balance.user_balance_entity import UserBalance
from source.transfer.domain.entities.transfer_entity import Transfer
from source.common_types.transfer_operation_types import TransferOperationType
from source.common_types.transfer_status_types import TransferStatusType
from uuid import uuid4
import aiohttp


class CryptoToFiatStrategy(ISwap):
    async def execute_swap(self, from_currency: str, to_currency: str, amount: float, balance: UserBalance) -> SwapResult:
        current_balance = balance.amount or Decimal("0")
        amount_decimal = Decimal(str(amount))
        
        if current_balance < amount_decimal:
            raise ValueError(f"Insufficient balance.")
        
        converted_amount = 0
        usd_amount = amount_decimal
        if CurrencyType(from_currency).is_fiat():
            if from_currency != CurrencyType.USD.value:
                usd_amount = await self._get_fiat_rate(from_currency, CurrencyType.USD.value) * amount_decimal 
            converted_amount = await self._get_crypto_rate(CurrencyType.USD.value, to_currency) * usd_amount

        if CurrencyType(from_currency).is_crypto():
            usd_amount = await self._get_crypto_rate(from_currency, CurrencyType.USD.value) * amount_decimal
            converted_amount = await self._get_fiat_rate(CurrencyType.USD.value, to_currency) * usd_amount

        current_time = datetime.now()
        reference = str(uuid4())

        debit_transfer = Transfer(
            type=TransferOperationType.SWAP.value,
            user_id=str(balance.user_id),
            status=TransferStatusType.CONFIRMED.value,
            reference=reference,
            created_at=current_time,
            amount=f"-{amount_decimal}",
            currency=from_currency
        )
        
        credit_transfer = Transfer(
            type=TransferOperationType.SWAP.value,
            user_id=str(balance.user_id),
            status=TransferStatusType.CONFIRMED.value,
            reference=reference,
            created_at=current_time,
            amount=str(converted_amount),
            currency=to_currency
        )
        
        return SwapResult(debit=debit_transfer, credit=credit_transfer)
    
    async def _get_crypto_rate(self, from_currency: str, to_currency: str) -> Decimal:
        COINGECKO_IDS = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "USD": "usd"
        }
        
        if from_currency not in COINGECKO_IDS:
            raise ValueError(f"Unsupported crypto currency: {from_currency}")
        
        try:
            async with aiohttp.ClientSession() as session:
                from_id = COINGECKO_IDS[from_currency]
                to_id = COINGECKO_IDS[to_currency]
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={from_id},{from_currency}&vs_currencies={to_currency},{to_id}"
                
                async with session.get(url) as response:
                    if response.status != 200:
                        raise ValueError("Failed to fetch exchange rate from CoinGecko")
                    
                    data = await response.json()
                    crypto_price_usd = Decimal(str(data[from_id][to_id])) | Decimal(str(data[from_currency][to_currency])) | Decimal(str(data[from_currency][to_id])) | Decimal(str(data[from_id][to_currency]))
                    
                    return crypto_price_usd
        
        except Exception as e:
            raise ValueError(f"Error fetching crypto exchange rate: {str(e)}")
    
    async def _get_fiat_rate(self, from_currency: str, to_currency: str) -> Decimal:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://dolarapi.com/v1/dolares/blue") as response:
                    if response.status != 200:
                        raise ValueError("Failed to fetch exchange rate from DolarAPI")
                    
                    data = await response.json()
                    venta_rate = Decimal(str(data["venta"]))
                    
                    if from_currency == "ARS" and to_currency == "USD":
                        return Decimal("1") / venta_rate
                    elif from_currency == "USD" and to_currency == "ARS":
                        return venta_rate
                    else:
                        raise ValueError(f"Unsupported currency pair: {from_currency} -> {to_currency}")
        
        except Exception as e:
            raise ValueError(f"Error fetching exchange rate: {str(e)}")