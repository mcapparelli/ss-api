from fastapi import HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.psql.db import get_db
from source.transfer.application.use_cases.swap.use_case import SwapUseCase

class SwapResponse(BaseModel):
    id: str
    type: str
    status: str
    amount: str
    currency: str
    created_at: str

class SwapRequest(BaseModel):
    user_id: str
    amount: str
    currency: str
    target_currency: str

async def swap(
    request: SwapRequest,
    db: AsyncSession = Depends(get_db)
):
    use_case = SwapUseCase(db)
    try:
        transaction = await use_case.execute(user_id=request.user_id, amount=request.amount, currency=request.currency, target_currency=request.target_currency)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    
    return SwapResponse(
        id=transaction.reference,
        type=transaction.type,
        status=transaction.status,
        currency=transaction.currency,
        created_at=transaction.created_at.isoformat(),
        amount=transaction.amount
    )
