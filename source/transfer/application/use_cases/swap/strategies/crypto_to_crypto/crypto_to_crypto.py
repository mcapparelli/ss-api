from decimal import Decimal
from datetime import datetime
from source.transfer.application.use_cases.swap.swap_result import SwapResult
from source.transfer.infrastructure.service.price_provider import PriceProvider
from ..swap_interface import ISwap
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
        
        exchange_rate = await PriceProvider.get_crypto_rate(from_currency, to_currency)
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