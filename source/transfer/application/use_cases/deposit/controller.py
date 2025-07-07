from decimal import Decimal
import uuid
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from source.common_types.currency_types import CurrencyType
from source.common_types.transfer_operation_types import TransferOperationType
from source.common_types.transfer_status_types import TransferStatusType
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.psql.db import get_db
from source.transfer.application.use_cases.deposit.use_case import DepositUseCase

class DepositResponse(BaseModel):
    id: str
    type: TransferOperationType = TransferOperationType.DEPOSIT
    user_id: str
    status: TransferStatusType
    created_at: str

class DepositRequest(BaseModel):
    user_id: uuid.UUID
    amount: Decimal
    currency: CurrencyType

async def deposit(
    request: DepositRequest,
    db: AsyncSession = Depends(get_db)
):
    use_case = DepositUseCase(db)
    try:
        transaction = await use_case.execute(user_id=request.user_id, amount=request.amount, currency=request.currency)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return DepositResponse(
        id=str(transaction.id),
        type=TransferOperationType.DEPOSIT.value,
        user_id=str(transaction.user_id),
        status=transaction.status,
        created_at=transaction.created_at.isoformat(),
    )
