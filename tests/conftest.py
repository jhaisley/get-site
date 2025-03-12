import pytest
from httpx import AsyncClient

@pytest.fixture
async def async_client():
    async with AsyncClient() as client:
        yield client