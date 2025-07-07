from fastapi import HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.psql.db import get_db
from source.transfer.application.use_cases.deposit.use_case import DepositUseCase

class DepositResponse(BaseModel):
    id: str
    type: str
    user_id: str
    status: str
    created_at: str

class DepositRequest(BaseModel):
    user_id: str
    amount: float
    currency: str

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
        type=transaction.type,
        user_id=str(transaction.user_id),
        status=transaction.status,
        created_at=transaction.created_at.isoformat(),
    )
