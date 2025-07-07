from decimal import Decimal
from source.transfer.application.use_cases.swap.strategies.swap_strategy_factory.swap_strategy_factory import SwapStrategyFactory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from source.user.domain.entities.user_entity import User
from source.user.domain.entities.user_balance.user_balance_entity import UserBalance
from source.transfer.domain.entities.transfer_entity import Transfer

class SwapUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, user_id: str, amount: str, currency: str, target_currency: str) -> Transfer:
        if currency == target_currency:
            raise ValueError("Source and destination currencies cannot be the same")
        
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError('User not found')
        
        result = await self.db.execute(
            select(UserBalance).where(UserBalance.user_id == user_id, UserBalance.currency == currency)
        )
        balance = result.scalar_one_or_none()
        if not balance:
            raise ValueError(f'Balance for {currency} not found')
        
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("Amount must be positive")
        
        swap_strategy = SwapStrategyFactory()
        transactions = await swap_strategy.execute_swap(currency, target_currency, float(amount_decimal), balance)
        
        result = await self.db.execute(
            select(UserBalance).where(UserBalance.user_id == user_id, UserBalance.currency == target_currency)
        )
        target_balance = result.scalar_one_or_none()
        if not target_balance:
           raise ValueError(f'Balance for {target_balance} not found')
        
        balance.decrement(abs(Decimal(transactions.debit.amount)))
        target_balance.increment(abs(Decimal(transactions.credit.amount)))

        self.db.add(balance)
        self.db.add(target_balance)
        self.db.add(transactions.debit)
        self.db.add(transactions.credit)
        await self.db.commit()
        
        return transactions.credit

