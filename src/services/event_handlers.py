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

from src.models.user_data import UserSettings
from src.models.alert import Alert
import httpx

async def handle_api_key_discovered(user_id: str, provider: str, repository: str, risk_level: str):
    """
    Handles API_KEY_DISCOVERED by:
    1. Creating an in-app Alert.
    2. Sending a Slack webhook if configured.
    """
    async with AsyncSessionLocal() as db:
        try:
            user_uuid = uuid.UUID(user_id)
            
            # 1. Create Alert
            alert_msg = f"Exposed {provider} key found in {repository}"
            alert = Alert(
                user_id=user_uuid,
                title="API Key Exposed!",
                message=alert_msg,
                type="security",
                severity=risk_level,
                status="unread"
            )
            db.add(alert)

            # 2. Check User Settings for notifications
            settings = await db.scalar(
                __import__("sqlalchemy").select(UserSettings).where(UserSettings.user_id == user_uuid)
            )
            
            if settings and settings.slack_webhook:
                # Send Slack webhook asynchronously
                async with httpx.AsyncClient() as client:
                    await client.post(
                        settings.slack_webhook,
                        json={
                            "text": f"🚨 *KeySentry Alert*\n{alert_msg}\nRisk Level: {risk_level.upper()}"
                        }
                    )
                    
            await db.commit()
            print(f"Handled API key discovery for user {user_id}")
        except Exception as e:
            await db.rollback()
            print(f"Failed to handle API_KEY_DISCOVERED for user {user_id}: {e}")

async def handle_scan_completed(user_id: str, scan_id: str, keys_found: int):
    async with AsyncSessionLocal() as db:
        try:
            if keys_found > 0:
                # We already alert per key, maybe we just want an informational alert if 0 keys were found
                pass
            else:
                alert = Alert(
                    user_id=uuid.UUID(user_id),
                    title="Scan Completed",
                    message="Scan completed successfully. No new keys found.",
                    type="info",
                    severity="low",
                    status="unread"
                )
                db.add(alert)
                await db.commit()
        except Exception as e:
            await db.rollback()
            print(f"Failed to handle SCAN_COMPLETED: {e}")

async def handle_scan_failed(user_id: str, scan_id: str, error: str):
    async with AsyncSessionLocal() as db:
        try:
            alert = Alert(
                user_id=uuid.UUID(user_id),
                title="Scan Failed",
                message=f"A background scan failed to complete. Error: {error or 'Unknown'}",
                type="system",
                severity="medium",
                status="unread"
            )
            db.add(alert)
            await db.commit()
        except Exception as e:
            await db.rollback()
            print(f"Failed to handle SCAN_FAILED: {e}")

def register_events():
    event_bus.subscribe(EventType.USER_SIGNED_UP, handle_user_signed_up)
    event_bus.subscribe(EventType.API_KEY_DISCOVERED, handle_api_key_discovered)
    event_bus.subscribe(EventType.SCAN_COMPLETED, handle_scan_completed)
    event_bus.subscribe(EventType.SCAN_FAILED, handle_scan_failed)
