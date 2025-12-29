from pydantic import BaseModel
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime

class TestRunBase(BaseModel):
    status: str = "PENDING"
    logs: List[Any] = []
    result_summary: Optional[str] = None

class TestRunCreate(BaseModel):
    case_id: UUID

class TestRunRead(TestRunBase):
    id: UUID
    case_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
