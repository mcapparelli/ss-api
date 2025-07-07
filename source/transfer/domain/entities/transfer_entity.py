import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from typing import Dict
from infrastructure.psql.db import Base

class Transfer(Base):
    __tablename__ = "transfer"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String, nullable=False)
    reference = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)
    

    def __init__(self, type: str, user_id: str, status: str, reference: str = None, created_at: str = None):
        self.type = type
        self.user_id = user_id
        self.status = status
        self.reference = reference
        if created_at:
            self.created_at = created_at

   
