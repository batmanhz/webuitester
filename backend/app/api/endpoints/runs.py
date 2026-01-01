from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from typing import List, Dict
from uuid import UUID
import json
import asyncio

from backend.app.models.test_run import TestRun
from backend.app.models.test_case import TestCase
from backend.app.schemas.test_run import TestRunCreate, TestRunRead
from backend.app.agent.core import Agent
from backend.app.core.socket_manager import manager

router = APIRouter()

# Store active run controls to allow stopping
# run_id -> {"stop_event": asyncio.Event, "task": asyncio.Task}
active_runs: Dict[str, dict] = {}

async def run_agent_task(run_id: UUID, case_id: UUID):
    stop_event = asyncio.Event()
    active_runs[str(run_id)] = {"stop_event": stop_event}
    
    try:
        run = await TestRun.get(id=run_id)
        case = await TestCase.get(id=case_id)
        
        run.status = "RUNNING"
        await run.save()
        
        await manager.broadcast(str(run_id), {"type": "status", "data": "RUNNING"})
        
        agent = Agent()
        
        async def log_callback(event: dict):
            try:
                # Broadcast to WS
                await manager.broadcast(str(run_id), event)
                
                # Append to DB logs (simple append, maybe inefficient for huge logs but fine for V1)
                if event["type"] == "log":
                    run.logs.append(event)
                    await run.save(update_fields=["logs"])
            except Exception as e:
                print(f"Log Callback Error: {e}")

        success = await agent.execute_case(case, log_callback, stop_event=stop_event)
        
        if stop_event.is_set():
            run.status = "STOPPED"
        else:
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
    finally:
        # Cleanup
        if str(run_id) in active_runs:
            del active_runs[str(run_id)]

@router.post("/", response_model=TestRunRead)
async def create_run(run_in: TestRunCreate, background_tasks: BackgroundTasks):
    case = await TestCase.get_or_none(id=run_in.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Test case not found")
        
    run = await TestRun.create(case=case, status="PENDING")
    
    # Start execution in background
    background_tasks.add_task(run_agent_task, run.id, case.id)
    
    return run

@router.post("/{run_id}/stop")
async def stop_run(run_id: UUID):
    run_id_str = str(run_id)
    if run_id_str in active_runs:
        active_runs[run_id_str]["stop_event"].set()
        return {"message": "Stop signal sent"}
    
    # If not in active memory, check DB
    run = await TestRun.get_or_none(id=run_id)
    if not run:
         raise HTTPException(status_code=404, detail="Test run not found")
    
    if run.status == "RUNNING":
        # It might be running but we lost track (e.g. restart)? 
        # Or it's a zombie state. Just mark it stopped.
        run.status = "STOPPED"
        await run.save()
        return {"message": "Run marked as stopped"}
        
    return {"message": "Run is not running"}

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
        # Send current status immediately upon connection
        # This fixes the race condition where frontend connects after RUNNING status broadcast
        run = await TestRun.get_or_none(id=UUID(run_id))
        if run:
            await websocket.send_json({"type": "status", "data": run.status})
            
            # Optionally send existing logs if client reconnects (simple version)
            # if run.logs:
            #     for log in run.logs:
            #         await websocket.send_json(log)

        while True:
            # Keep connection alive, maybe handle client messages if needed
            # For now, just listen (we assume client doesn't send much)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(run_id, websocket)
    except Exception as e:
        print(f"WebSocket Error: {e}")
        manager.disconnect(run_id, websocket)
