from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from typing import List
from uuid import UUID
import json
import asyncio

from backend.app.models.test_run import TestRun
from backend.app.models.test_case import TestCase
from backend.app.schemas.test_run import TestRunCreate, TestRunRead
from backend.app.agent.core import Agent
from backend.app.core.socket_manager import manager

router = APIRouter()

async def run_agent_task(run_id: UUID, case_id: UUID):
    try:
        run = await TestRun.get(id=run_id)
        case = await TestCase.get(id=case_id)
        
        run.status = "RUNNING"
        await run.save()
        
        await manager.broadcast(str(run_id), {"type": "status", "data": "RUNNING"})
        
        agent = Agent()
        
        async def log_callback(event: dict):
            # Broadcast to WS
            await manager.broadcast(str(run_id), event)
            
            # Append to DB logs (simple append, maybe inefficient for huge logs but fine for V1)
            # We assume event is JSON serializable
            # For screenshot (base64), we might not want to save to DB logs field if it's too huge, 
            # but for now let's save text logs only? Or everything?
            # Story says "Stream execution logs and screenshots".
            # Saving base64 images to JSON column in DB is bad practice. 
            # For history, maybe we just save text logs.
            if event["type"] == "log":
                run.logs.append(event)
                await run.save(update_fields=["logs"])

        success = await agent.execute_case(case, log_callback)
        
        run.status = "PASSED" if success else "FAILED"
        await run.save()
        await manager.broadcast(str(run_id), {"type": "status", "data": run.status})
        
    except Exception as e:
        print(f"Background Task Error: {e}")
        run = await TestRun.get(id=run_id)
        run.status = "FAILED"
        run.result_summary = str(e)
        await run.save()
        await manager.broadcast(str(run_id), {"type": "error", "data": str(e)})

@router.post("/", response_model=TestRunRead)
async def create_run(run_in: TestRunCreate, background_tasks: BackgroundTasks):
    case = await TestCase.get_or_none(id=run_in.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Test case not found")
        
    run = await TestRun.create(case=case, status="PENDING")
    
    # Start execution in background
    background_tasks.add_task(run_agent_task, run.id, case.id)
    
    return run

@router.get("/{run_id}", response_model=TestRunRead)
async def get_run(run_id: UUID):
    run = await TestRun.get_or_none(id=run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Test run not found")
    return run

@router.websocket("/ws/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    await manager.connect(run_id, websocket)
    try:
        while True:
            # Keep connection alive, maybe handle client messages if needed
            # For now, just listen (we assume client doesn't send much)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(run_id, websocket)
    except Exception as e:
        print(f"WebSocket Error: {e}")
        manager.disconnect(run_id, websocket)
