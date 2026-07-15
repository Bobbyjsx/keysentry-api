import asyncio
import os
import asyncpg

async def main():
    db_url = os.environ.get("DATABASE_URL")
    db_url = db_url.replace("postgresql+asyncpg", "postgresql")
    conn = await asyncpg.connect(db_url)
    try:
        records = await conn.fetch("SELECT * FROM alerts ORDER BY created_at DESC LIMIT 5;")
        print(f"Alerts: {len(records)}")
        for r in records:
            print(dict(r))
    except Exception as e:
        print("Error:", e)
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
