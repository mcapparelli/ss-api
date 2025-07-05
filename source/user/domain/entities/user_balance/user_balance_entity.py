from sqlalchemy import Column,  Integer, Numeric, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from enum import Enum
from typing import Dict
from decimal import Decimal, InvalidOperation
from common_types.currency_types import Currency

Base = declarative_base()

class UserBalance(Base):
    __tablename__ = "user_balance"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    currency = Column(Enum(Currency), nullable=False)
    amount = Column(Numeric(precision=18, scale=8), default=0)
    user = relationship("User", back_populates="balances")

    def __repr__(self):
        return f"<UserBalance(user_id={self.user_id}, currency={self.currency}, amount={self.amount})>"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "currency": self.currency.value,
            "amount": float(self.amount) if self.amount else 0.0
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'UserBalance':
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id"),
            currency=Currency(data.get("currency")),
            amount=Decimal(str(data.get("amount", 0)))
        )

    def increment(self, amount: float) -> None:
        try:
            amount_decimal = Decimal(str(amount))
            if amount_decimal < 0:
                raise ValueError("Amount to increment must be positive")
            
            current_amount = self.amount or Decimal('0')
            self.amount = current_amount + amount_decimal
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"Error incrementing balance: {e}")

    def decrement(self, amount: float) -> None:
        try:
            amount_decimal = Decimal(str(amount))
            if amount_decimal < 0:
                raise ValueError("Amount to decrement must be positive")
            
            current_amount = self.amount or Decimal('0')
            if current_amount < amount_decimal:
                raise ValueError(f"Insufficient balance. Available: {current_amount}, Required: {amount_decimal}")
            
            self.amount = current_amount - amount_decimal
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"Error decrementing balance: {e}")