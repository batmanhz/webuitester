import os
from tortoise import Tortoise

DB_URL = "sqlite://:memory:" if os.getenv("TEST_MODE") else "sqlite://webuitester.db"

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
