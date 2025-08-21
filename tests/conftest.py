"""
Full integration Pytest configuration and fixtures for Sign Glove API.
This uses MongoDB Atlas directly (test DB), wipes data before each test,
and seeds an admin user.
"""
from pathlib import Path
import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient
import sys, os 
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from backend.main import app
from backend.core.auth import pwd_context, create_access_token, UserRole
from backend.core.database import client as mongo_client, users_collection
import tempfile
import shutil


# ------------------ ENVIRONMENT ------------------
# Ensure repository backend root is importable
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Force test environment
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("DB_NAME", "signglove_test")  # Atlas test DB name


# ------------------ EVENT LOOP ------------------
@pytest.fixture(scope="session")
def event_loop():
    """Create a session-wide event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ------------------ TEST CLIENT ------------------
@pytest_asyncio.fixture
async def async_client():
    """Async test client for FastAPI app (real integration)."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ------------------ AUTH TOKENS ------------------
@pytest.fixture
def admin_token():
    return create_access_token(data={"sub": "admin", "role": UserRole.ADMIN})

@pytest.fixture
def user_token():
    return create_access_token(data={"sub": "user", "role": UserRole.USER})

@pytest.fixture
def viewer_token():
    return create_access_token(data={"sub": "viewer", "role": UserRole.VIEWER})

@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def user_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}

@pytest.fixture
def viewer_headers(viewer_token):
    return {"Authorization": f"Bearer {viewer_token}"}


# ------------------ SAMPLE DATA ------------------
@pytest.fixture
def sample_sensor_data():
    return {
        "flex_sensors": [0.1, 0.2, 0.3, 0.4, 0.5],
        "imu_data": [0.6, 0.7, 0.8, 0.9, 1.0, 1.1],
        "gesture_label": "hello",
        "session_id": "test_session_123"
    }

@pytest.fixture
def sample_gesture_session():
    return {
        "session_id": "test_session_123",
        "timestamp": "2024-01-01T12:00:00Z",
        "sensor_values": [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1]],
        "gesture_label": "hello",
        "device_info": {"source": "test", "device_id": "test-glove-01"}
    }

@pytest.fixture
def sample_training_result():
    return {
        "session_id": "training_123",
        "timestamp": "2024-01-01T12:00:00Z",
        "accuracy": 0.95,
        "model_name": "test_model.tflite",
        "notes": "Test training session"
    }

@pytest.fixture
def temp_data_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


# ------------------ DB CLEANUP + SEED ------------------
@pytest_asyncio.fixture(autouse=True, scope="function")
async def clean_and_seed_db():
    """
    Before each test:
      - Drop all collections in the test DB
      - Seed an admin user
    After each test:
      - Drop all collections again
    """
    db_name = os.getenv("DB_NAME", "signglove_test")
    db = mongo_client[db_name]

    # Drop all collections (clean state)
    collections = await db.list_collection_names()
    for col in collections:
        await db.drop_collection(col)

    # Seed admin user
    hashed = pwd_context.hash("admin123")
    await users_collection.insert_one({
        "email": "admin@signglove.com",
        "password_hash": hashed,
        "role": "admin"
    })

    yield

    # Cleanup again after test
    collections = await db.list_collection_names()
    for col in collections:
        await db.drop_collection(col)


# ------------------ PYTEST MARKERS ------------------
def pytest_configure(config):
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "auth: mark test as authentication test")
