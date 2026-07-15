import asyncio
import os
import uuid
from src.services.event_handlers import handle_api_key_discovered

async def main():
    try:
        user_id = str(uuid.uuid4())
        await handle_api_key_discovered(
            user_id=user_id,
            provider="TestProvider",
            repository="TestRepo",
            risk_level="high"
        )
        print("Success")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
