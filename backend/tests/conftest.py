import os
# Set env var before importing anything else
os.environ["TEST_MODE"] = "1"

import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from tortoise import Tortoise

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="function")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

@pytest.fixture(scope="function", autouse=True)
async def initialize_tests(request):
    config = {
        "connections": {"default": "sqlite://:memory:"},
        "apps": {
            "models": {
                "models": ["backend.app.models.test_case", "backend.app.models.test_run"],
                "default_connection": "default",
            }
        }
    }
    await Tortoise.init(config=config)
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()
