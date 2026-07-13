import asyncio
from src.core.database import engine
from src.models import api_key, alert, user_data
from src.core.database import Base

async def init_models():
    async with engine.begin() as conn:
        print("Creating tables...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created.")

asyncio.run(init_models())
