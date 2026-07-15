from src.core.database import Base, get_db
from src.main import app
import asyncio
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env.test"), override=True)

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://keysentry_admin:ziz!qak-pinnaT-7wy*zze@100.76.107.7:6432/postgres",
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        execution_options={"schema_translate_map": {None: "test_schema"}},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    yield
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        execution_options={"schema_translate_map": {None: "test_schema"}},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session():
    # Function scoped engine, bound to the test's event loop
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        execution_options={"schema_translate_map": {None: "test_schema"}},
    )
    TestingSessionLocal = async_sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    async with TestingSessionLocal() as session:
        yield session
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(text(f"TRUNCATE test_schema.{table.name} CASCADE;"))
        await session.commit()
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
