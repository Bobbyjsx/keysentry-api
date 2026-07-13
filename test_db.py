import asyncio
from src.core.database import AsyncSessionLocal
from sqlalchemy import text
from src.core.config import settings

async def test_conn():
    print("Trying:", settings.DATABASE_URL)
    async with AsyncSessionLocal() as session:
        try:
            res = await session.execute(text("SELECT 1"))
            print("DB Connection Success:", res.scalar())
        except Exception as e:
            print("DB Error:", e)

asyncio.run(test_conn())
