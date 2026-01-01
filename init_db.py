import asyncio
from tortoise import Tortoise
from backend.app.core.database import TORTOISE_ORM

async def init():
    print("Initializing Tortoise ORM...")
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        print("Tortoise initialized.")
        
        print("Generating schemas...")
        await Tortoise.generate_schemas()
        print("Schema generated successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Closing database connections...")
        await Tortoise.close_connections()
        print("Connections closed.")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.getcwd())
    
    # Windows-specific event loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    asyncio.run(init())
