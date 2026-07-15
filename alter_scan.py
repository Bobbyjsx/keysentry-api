import asyncio
import os
import asyncpg

async def main():
    db_url = os.environ.get("DATABASE_URL")
    db_url = db_url.replace("postgresql+asyncpg", "postgresql")
    conn = await asyncpg.connect(db_url)
    try:
        await conn.execute("ALTER TABLE scan_history ADD COLUMN IF NOT EXISTS sources JSONB NOT NULL DEFAULT '[]'::jsonb;")
        print("Altered scan_history table to add sources.")
    except Exception as e:
        print("Error:", e)
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
