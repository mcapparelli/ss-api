from typing import Dict
from source.user.domain.entities.user_entity import User
from source.user.domain.services.user_factory import create_user
from sqlalchemy.ext.asyncio import AsyncSession

class CreateUserUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, name: str) -> User:
        user = create_user(name)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user, attribute_names=['balances'])
        return user