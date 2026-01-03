import sys
import asyncio

# Force ProactorEventLoop on Windows - CRITICAL for Playwright
# This must run before any async loop is created
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from backend.app.core.database import TORTOISE_ORM
from backend.app.api.endpoints import test_cases, runs, config
from backend.app.core.patches import apply_browser_use_patches

# Apply patches to external libraries
apply_browser_use_patches()

app = FastAPI(title="WebuiTester API", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routes
app.include_router(test_cases.router, prefix="/api", tags=["Test Cases"])
app.include_router(runs.router, prefix="/api/runs", tags=["Test Runs"])
app.include_router(config.router, prefix="/api", tags=["Configuration"])

# Database
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True, # Auto-create tables for now
    add_exception_handlers=True,
)

@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_running_loop()
    print(f"DEBUG: Current Event Loop: {type(loop)}")

@app.get("/")
async def root():
    return {"message": "Welcome to WebuiTester API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
