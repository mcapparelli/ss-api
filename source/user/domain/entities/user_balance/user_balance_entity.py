import decimal
from sqlalchemy import Column, Integer, Numeric, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from decimal import Decimal
from infrastructure.psql.db import Base

class UserBalance(Base):
    __tablename__ = "user_balance"

    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    currency = Column(String, nullable=False)
    amount = Column(Numeric(precision=18, scale=8), default=0)
    user = relationship("User", back_populates="balances")

    def increment(self, amount: str) -> None:
        try:
            amt = Decimal(amount)
        except (ValueError, decimal.InvalidOperation):
            raise ValueError("Error incrementing balance")
        
        if amt < 0:
            raise ValueError("Amount to increment must be positive")
        self.amount = (self.amount or Decimal("0")) + amt

    def decrement(self, amount: str) -> None:
        try:
            amt = Decimal(amount)
        except (ValueError, decimal.InvalidOperation):
            raise ValueError("Error decrementing balance")
        
        if amt < 0:
            raise ValueError("Amount to decrement must be positive")
        current = self.amount or Decimal("0")
        if current < amt:
            raise ValueError(f"Insufficient balance. Available: {current}, Required: {amt}")
        self.amount = current - amt
