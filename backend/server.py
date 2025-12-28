import uvicorn
import sys
import asyncio
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.app.core.config import settings

if __name__ == "__main__":
    # Force policy here for the main process
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Reload functionality needs string import for 'app'
    # On Windows, 'reload=True' spawns subprocesses which might default back to SelectorEventLoop
    # unless we carefully control it. For production/stability, reload=False is safer.
    # If reload=True is needed, we must ensure the subprocess also sets the policy.
    # Uvicorn's 'loop="asyncio"' uses the default policy set above.
    uvicorn.run("backend.main:app", host=settings.server.host, port=settings.server.port, reload=False, loop="asyncio")
