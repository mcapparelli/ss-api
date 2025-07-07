import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from typing import Dict
from infrastructure.psql.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    balances = relationship("UserBalance", back_populates="user", cascade="all, delete-orphan")

    def __init__(self, name: str):
        self.name = name

    def to_dict(self) -> Dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "balances": [b.to_dict() for b in self.balances]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "User":
        user = cls(name=data["name"])
        if data.get("id"):
            user.id = uuid.UUID(data["id"])
        return user
