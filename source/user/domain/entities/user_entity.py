from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base, relationship
from typing import Dict 

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    balances = relationship("UserBalance", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}')>"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "balances": [balance.to_dict() for balance in self.balances]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        return cls(
            id=data.get("id"),
            name=data.get("name")
        )
