import asyncio
import time
from uuid import UUID
from typing import List

from src.worker.celery_app import celery_app
from src.lib.git_engine import GitEngine
from src.core.database import AsyncSessionLocal
from src.models.user_data import ScanHistory
from src.models.api_key import APIKey
from src.schemas.api_key import APIKeyCreate
from src.repositories.user_data import UserDataRepository
from src.repositories.api_key import APIKeyRepository
from sqlalchemy import select, update

async def _process_scan(scan_id: UUID, user_id: UUID, github_token: str, repository: str):
    async with AsyncSessionLocal() as session:
        # 1. Instantiate the Engine
        engine = GitEngine(github_token)
        
        start_time = time.time()
        
        # 2. Run the scan (synchronous blocking call runs inside the async wrapper, 
        # which is acceptable for a dedicated celery worker process)
        discovered = engine.scan_repository(repository)
        duration = int(time.time() - start_time)
        
        # 3. Save discovered keys
        api_key_repo = APIKeyRepository(session)
        for key_data in discovered:
            key_in = APIKeyCreate(
                user_id=user_id,
                key_hash=key_data["key_hash"],
                provider=key_data["provider"],
                source=key_data["source"],
                link=key_data["link"],
                repository=key_data["repository"],
                status="active"
            )
            await api_key_repo.create(key_in)
            
        # 4. Update the ScanHistory status
        stmt = (
            update(ScanHistory)
            .where(ScanHistory.id == scan_id)
            .values(
                status="completed",
                keys_found=len(discovered),
                sources_scanned=1, # simplified
                duration_seconds=duration
            )
        )
        await session.execute(stmt)
        await session.commit()
        
        return {"scan_id": str(scan_id), "keys_found": len(discovered), "duration": duration}

@celery_app.task(name="tasks.run_github_scan")
def run_github_scan(scan_id_str: str, user_id_str: str, github_token: str, repository: str):
    """
    Celery task that runs the GitHub scan using the GitEngine.
    """
    scan_id = UUID(scan_id_str)
    user_id = UUID(user_id_str)
    
    # Run the async database operations within the sync celery task
    result = asyncio.run(_process_scan(scan_id, user_id, github_token, repository))
    return result
