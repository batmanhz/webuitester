from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID
from backend.app.models.test_case import TestCase, TestStep
from backend.app.schemas.test_case import TestCaseCreate, TestCaseRead, TestStepCreate, TestCaseUpdate
from tortoise.transactions import in_transaction

router = APIRouter()

@router.get("/cases", response_model=List[TestCaseRead])
async def get_test_cases():
    return await TestCase.all().prefetch_related("steps")

@router.post("/cases", response_model=TestCaseRead)
async def create_test_case(case_in: TestCaseCreate):
    case = await TestCase.create(name=case_in.name, url=case_in.url)
    
    # Create steps
    for step_in in case_in.steps:
        await TestStep.create(
            case=case,
            order=step_in.order,
            instruction=step_in.instruction,
            expected_result=step_in.expected_result
        )
    
    # Refresh to get steps
    await case.fetch_related("steps")
    return case

@router.put("/cases/{case_id}", response_model=TestCaseRead)
async def update_test_case(case_id: UUID, case_in: TestCaseUpdate):
    case = await TestCase.get_or_none(id=case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    async with in_transaction():
        # Update basic info
        case.name = case_in.name
        case.url = case_in.url
        await case.save()
        
        # Replace steps (simplest strategy: delete all and recreate)
        # In a more complex scenario, we might want to update existing steps by ID
        await TestStep.filter(case_id=case_id).delete()
        
        for step_in in case_in.steps:
            await TestStep.create(
                case=case,
                order=step_in.order,
                instruction=step_in.instruction,
                expected_result=step_in.expected_result
            )
            
    await case.fetch_related("steps")
    return case

@router.get("/cases/{case_id}", response_model=TestCaseRead)
async def get_test_case(case_id: UUID):
    case = await TestCase.get_or_none(id=case_id).prefetch_related("steps")
    if not case:
        raise HTTPException(status_code=404, detail="Test case not found")
    return case

@router.delete("/cases/{case_id}", status_code=204)
async def delete_test_case(case_id: UUID):
    case = await TestCase.get_or_none(id=case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Test case not found")
    await case.delete()
    return
