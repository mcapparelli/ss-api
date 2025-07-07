from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from source.user.domain.entities.user_entity import User
from source.user.domain.entities.user_balance.user_balance_entity import UserBalance
from source.transfer.domain.entities.transfer_entity import Transfer
from source.common_types.transfer_operation_types import TransferOperationType
from source.common_types.transfer_status_types import TransferStatusType

class DepositUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, user_id: str, amount: float, currency: str) -> Transfer:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError('User not found')


        result = await self.db.execute(
            select(UserBalance).where(UserBalance.user_id == user_id, UserBalance.currency == currency)
        )
        balance = result.scalar_one_or_none()
        if not balance:
            raise ValueError('Balance for currency not found')
        balance.increment(str(amount))

        transfer = Transfer(
            type=TransferOperationType.DEPOSIT.value,
            user_id=user_id,
            status=TransferStatusType.CONFIRMED.value,
            reference=None,
            created_at=datetime.utcnow()
        )
        
        self.db.add(transfer)
        self.db.add(balance)
        await self.db.commit()
        await self.db.refresh(transfer)

        return transfer