import uuid
from src.core.events import event_bus, EventType
from src.core.database import AsyncSessionLocal
from src.models.user_data import Profile

async def handle_user_signed_up(user_id_str: str, email: str, full_name: str):
    """
    Handles the USER_SIGNED_UP event by creating the necessary Profile record.
    UserSettings will be created lazily when accessed.
    """
    async with AsyncSessionLocal() as db:
        try:
            profile = Profile(
                id=uuid.UUID(user_id_str),
                full_name=full_name,
                username=email.split('@')[0]
            )
            db.add(profile)
            await db.commit()
            print(f"Profile created successfully for user {user_id_str}")
        except Exception as e:
            await db.rollback()
            print(f"Failed to create profile for user {user_id_str}: {e}")

def register_events():
    event_bus.subscribe(EventType.USER_SIGNED_UP, handle_user_signed_up)
