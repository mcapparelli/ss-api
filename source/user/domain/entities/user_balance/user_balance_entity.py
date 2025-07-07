import uuid
from sqlalchemy import Column, Integer, Numeric, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from typing import Dict
from decimal import Decimal
from infrastructure.psql.db import Base

class UserBalance(Base):
    __tablename__ = "user_balance"

    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    currency = Column(String, nullable=False)
    amount = Column(Numeric(precision=18, scale=8), default=0)
    user = relationship("User", back_populates="balances")

    def __repr__(self):
        return f"<UserBalance(user_id={self.user_id}, currency={self.currency}, amount={self.amount})>"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "user_id": str(self.user_id),
            "currency": self.currency,
            "amount": float(self.amount or 0)
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "UserBalance":
        ub = cls(
            user_id=uuid.UUID(data["user_id"]),
            currency=data["currency"],
            amount=Decimal(str(data.get("amount", 0)))
        )
        if data.get("id"):
            ub.id = data["id"]
        return ub

    def increment(self, amount: float) -> None:
        amt = Decimal(str(amount))
        if amt < 0:
            raise ValueError("Amount to increment must be positive")
        self.amount = (self.amount or Decimal("0")) + amt

    def decrement(self, amount: float) -> None:
        amt = Decimal(str(amount))
        if amt < 0:
            raise ValueError("Amount to decrement must be positive")
        current = self.amount or Decimal("0")
        if current < amt:
            raise ValueError(f"Insufficient balance. Available: {current}, Required: {amt}")
        self.amount = current - amt
