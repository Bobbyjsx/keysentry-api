import asyncio
import os
import asyncpg
from urllib.parse import urlparse

async def main():
    db_url = os.environ.get("DATABASE_URL")
    db_url = db_url.replace("postgresql+asyncpg", "postgresql")
    conn = await asyncpg.connect(db_url)
    try:
        # Check if we have any keys with a scan_id
        records = await conn.fetch("SELECT * FROM api_keys WHERE scan_id IS NOT NULL;")
        print(f"Keys with scan_id: {len(records)}")
        for r in records:
            print(r)
    except Exception as e:
        print("Error:", e)
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
