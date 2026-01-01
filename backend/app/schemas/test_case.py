from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class TestStepBase(BaseModel):
    order: int
    instruction: str
    expected_result: Optional[str] = None

class TestStepCreate(TestStepBase):
    pass

class TestStepRead(TestStepBase):
    id: UUID
    case_id: UUID

    model_config = ConfigDict(from_attributes=True)

class TestCaseBase(BaseModel):
    name: str
    url: str

class TestCaseCreate(TestCaseBase):
    steps: List[TestStepCreate] = []

class TestCaseUpdate(TestCaseBase):
    steps: List[TestStepCreate] = []

class TestCaseRead(TestCaseBase):
    id: UUID
    created_at: datetime
    steps: List[TestStepRead] = []

    model_config = ConfigDict(from_attributes=True)

class GenerateStepsRequest(BaseModel):
    url: str
    intent: str

class GenerateStepsResponse(BaseModel):
    name: str
    steps: List[TestStepCreate]
