from fastapi import HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.psql.db import get_db
from source.transfer.application.use_cases.history.use_case import HistoryUseCase
from source.transfer.domain.entities.transfer_entity import Transfer

class HistoryResponse(BaseModel):
    transactions: list[dict]

async def history(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    use_case = HistoryUseCase(db)
    try:
        transactions = await use_case.execute(user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return HistoryResponse(
        transactions=[{
            "id": str(t.id),
            "type": t.type,
            "user_id": str(t.user_id),
            "status": t.status,
            "created_at": t.created_at.isoformat() if t.created_at else None
        } for t in transactions]
    )
