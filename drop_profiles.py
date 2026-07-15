import asyncio
import os
import asyncpg

async def main():
    db_url = os.environ.get("DATABASE_URL")
    db_url = db_url.replace("postgresql+asyncpg", "postgresql")
    conn = await asyncpg.connect(db_url)
    try:
        # Drop foreign keys constraint first
        await conn.execute("ALTER TABLE scan_history DROP CONSTRAINT IF EXISTS scan_history_user_id_fkey;")
        await conn.execute("ALTER TABLE user_settings DROP CONSTRAINT IF EXISTS user_settings_user_id_fkey;")
        await conn.execute("ALTER TABLE api_keys DROP CONSTRAINT IF EXISTS api_keys_user_id_fkey;")
        await conn.execute("ALTER TABLE alerts DROP CONSTRAINT IF EXISTS alerts_user_id_fkey;")
        # Drop the table
        await conn.execute("DROP TABLE IF EXISTS profiles CASCADE;")
        print("Dropped profiles table and related constraints.")
    except Exception as e:
        print("Error:", e)
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
