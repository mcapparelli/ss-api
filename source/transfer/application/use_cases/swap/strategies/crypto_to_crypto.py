from decimal import Decimal
from datetime import datetime
from source.transfer.application.use_cases.swap.swap_result import SwapResult
from .swap_interface import ISwap
from source.user.domain.entities.user_balance.user_balance_entity import UserBalance
from source.transfer.domain.entities.transfer_entity import Transfer
from source.common_types.transfer_operation_types import TransferOperationType
from source.common_types.transfer_status_types import TransferStatusType
from uuid import uuid4
import aiohttp


class CryptoToCryptoStrategy(ISwap):
    async def execute_swap(self, from_currency: str, to_currency: str, amount: float, balance: UserBalance) -> SwapResult:
        current_balance = balance.amount or Decimal("0")
        amount_decimal = Decimal(str(amount))
        
        if current_balance < amount_decimal:
            raise ValueError(f"Insufficient balance.")
        
        exchange_rate = await self._get_exchange_rate(from_currency, to_currency)
        converted_amount = amount_decimal * exchange_rate
        
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
    
    async def _get_exchange_rate(self, from_currency: str, to_currency: str) -> Decimal:
        COINGECKO_IDS = {
            "BTC": "btc",
            "ETH": "eth"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                from_id = COINGECKO_IDS[from_currency]
                to_id = COINGECKO_IDS[to_currency]
                
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={from_id},{to_id}&vs_currencies=usd"
                
                async with session.get(url) as response:
                    if response.status != 200:
                        raise ValueError("Failed to fetch exchange rate from CoinGecko")
                    
                    data = await response.json()
                    
                    from_price_usd = Decimal(str(data[from_id]["usd"]))
                    to_price_usd = Decimal(str(data[to_id]["usd"]))
                    
                    exchange_rate = from_price_usd / to_price_usd
                    
                    return exchange_rate
        
        except Exception as e:
            raise ValueError(f"Error fetching exchange rate from CoinGecko: {str(e)}")