import asyncio
import os
import asyncpg
from urllib.parse import urlparse

async def main():
    db_url = os.environ.get("DATABASE_URL")
    db_url = db_url.replace("postgresql+asyncpg", "postgresql")
    conn = await asyncpg.connect(db_url)
    try:
        # Check if we can insert with string
        await conn.execute("SELECT * FROM scan_history LIMIT 1;")
        print("Connected.")
    except Exception as e:
        print("Error:", e)
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
