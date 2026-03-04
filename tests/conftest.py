"""
pytest conftest — reconnects to MongoDB for each test function to avoid
asyncio event-loop cross-contamination with Motor.
"""
import pytest_asyncio
from app.core.database import connect_db, disconnect_db, db_instance


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Connect a fresh Motor client per test function."""
    # Disconnect any existing client first
    if db_instance.client:
        db_instance.client.close()
        db_instance.client = None
        db_instance.db = None

    await connect_db()
    yield
    if db_instance.client:
        db_instance.client.close()
        db_instance.client = None
        db_instance.db = None
