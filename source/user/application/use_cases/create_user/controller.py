from fastapi import HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from source.user.application.use_cases.create_user.use_case import CreateUserUseCase
from infrastructure.psql.db import get_db

class UserResponse(BaseModel):
    id: str
    name: str
    balance: list

class CreateUserRequest(BaseModel):
    name: str

async def create_user(
    request: CreateUserRequest,
    db: AsyncSession = Depends(get_db)
):
    use_case = CreateUserUseCase(db)
    try:
        user = await use_case.execute(name=request.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return UserResponse(
        id=str(user.id),
        name=user.name,
        balance=[{"currency": b.currency, "amount": float(b.amount or 0)} for b in user.balances]
    )
