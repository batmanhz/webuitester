import asyncio
import httpx
import websockets
import json
import sys

BASE_URL = "http://localhost:19000/api"
WS_URL = "ws://localhost:19000/api/runs/ws"

async def run_qa():
    print("--- Starting Story 2.3 QA ---")
    
    async with httpx.AsyncClient() as client:
        # 1. Create Test Case
        print("[1] Creating Test Case...")
        case_payload = {
            "name": "Story 2.3 WS Test",
            "url": "https://www.baidu.com",
            "steps": [
                {
                    "instruction": "Type 'WebSocket' in search",
                    "expected_result": "Input filled",
                    "order": 1
                }
            ]
        }
        resp = await client.post(f"{BASE_URL}/cases", json=case_payload)
        if resp.status_code != 200:
            print(f"❌ Failed to create case: {resp.text}")
            return
        case_data = resp.json()
        case_id = case_data["id"]
        print(f"    ✅ Case Created: {case_id}")

        # 2. Create Test Run
        print("[2] Creating Test Run...")
        run_payload = {"case_id": case_id}
        resp = await client.post(f"{BASE_URL}/runs/", json=run_payload)
        if resp.status_code != 200:
            print(f"❌ Failed to create run: {resp.text}")
            return
        run_data = resp.json()
        run_id = run_data["id"]
        print(f"    ✅ Run Created: {run_id}")

    # 3. Connect WebSocket
    print(f"[3] Connecting to WebSocket: {WS_URL}/{run_id} ...")
    try:
        async with websockets.connect(f"{WS_URL}/{run_id}") as ws:
            print("    ✅ Connected!")
            
            # Listen for logs
            while True:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=30.0)
                    data = json.loads(message)
                    type = data.get("type")
                    content = data.get("data")
                    
                    if type == "log":
                        print(f"    [LOG] {content}")
                        if "Test Case execution completed" in str(content):
                            print("    ✅ Execution Success Message Received!")
                            break
                    elif type == "status":
                        print(f"    [STATUS] {content}")
                    elif type == "screenshot":
                        print(f"    [SCREENSHOT] Received (size: {len(content)} chars)")
                    elif type == "step_start":
                        print(f"    [STEP] Start Step {content['order']}")
                    elif type == "step_end":
                        print(f"    [STEP] End Step")
                    elif type == "error":
                        print(f"    ❌ Error: {content}")
                        break
                        
                except asyncio.TimeoutError:
                    print("    ⚠️ Timeout waiting for logs")
                    break
                except websockets.exceptions.ConnectionClosed:
                    print("    ⚠️ Connection Closed")
                    break
                    
    except Exception as e:
        print(f"❌ WebSocket Failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_qa())
