from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from source.user.domain.entities.user_entity import User
from source.user.domain.entities.user_balance.user_balance_entity import UserBalance
from source.transfer.domain.entities.transfer_entity import Transfer
from source.common_types.transfer_operation_types import TransferOperationType
from source.common_types.transfer_status_types import TransferStatusType

class HistoryUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, user_id: str) -> list[Transfer]:
        result = await self.db.execute(select(Transfer).where(Transfer.user_id == user_id))
        return result.scalars().all()