import os
from pathlib import Path
from tortoise import Tortoise

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_FILE = BASE_DIR / "webuitester.db"

DB_URL = "sqlite://:memory:" if os.getenv("TEST_MODE") else f"sqlite://{DB_FILE}"

TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": ["backend.app.models.test_case", "backend.app.models.test_run", "aerich.models"],
            "default_connection": "default",
        },
    },
}

async def init():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
