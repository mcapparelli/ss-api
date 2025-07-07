from decimal import Decimal
from datetime import datetime
from source.common_types.currency_types import CurrencyType
from source.transfer.application.use_cases.swap.swap_result import SwapResult
from .swap_interface import ISwap
from source.user.domain.entities.user_balance.user_balance_entity import UserBalance
from source.transfer.domain.entities.transfer_entity import Transfer
from source.common_types.transfer_operation_types import TransferOperationType
from source.common_types.transfer_status_types import TransferStatusType
from source.transfer.infrastructure.service.price_provider import PriceProvider
from uuid import uuid4


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
                usd_amount = await PriceProvider.get_fiat_rate(from_currency, CurrencyType.USD.value) * amount_decimal 
            converted_amount = await PriceProvider.get_crypto_rate(CurrencyType.USD.value, to_currency) * usd_amount

        if CurrencyType(from_currency).is_crypto():
            usd_amount = await PriceProvider.get_crypto_rate(from_currency, CurrencyType.USD.value) * amount_decimal
            converted_amount = await PriceProvider.get_fiat_rate(CurrencyType.USD.value, to_currency) * usd_amount

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