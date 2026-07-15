import asyncio
import os
import asyncpg
from urllib.parse import urlparse

async def main():
    db_url = os.environ.get("DATABASE_URL")
    # replace +asyncpg
    db_url = db_url.replace("postgresql+asyncpg", "postgresql")
    conn = await asyncpg.connect(db_url)
    try:
        await conn.execute("ALTER TABLE api_keys ADD COLUMN scan_id UUID REFERENCES scan_history(id) ON DELETE SET NULL;")
        print("Column added successfully.")
    except Exception as e:
        print("Error:", e)
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
