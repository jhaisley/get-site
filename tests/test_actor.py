import pytest
from pathlib import Path
from src.main import run_apify_actor, AsyncWebCrawler

@pytest.fixture
def mock_actor_input(monkeypatch):
    async def mock_get_input():
        return {
            'start_urls': [{'url': 'https://example.com'}],
            'max_depth': 2
        }
    monkeypatch.setattr('apify.Actor.get_input', mock_get_input)

@pytest.fixture
def mock_push_data(monkeypatch):
    async def mock_push(*args, **kwargs):
        return True
    monkeypatch.setattr('apify.Actor.push_data', mock_push)

@pytest.fixture
def mock_request_queue(monkeypatch):
    class MockQueue:
        async def add_request(self, *args, **kwargs):
            return True
        
    async def mock_open_queue(*args, **kwargs):
        return MockQueue()
    monkeypatch.setattr('apify.Actor.open_request_queue', mock_open_queue)

@pytest.mark.asyncio
async def test_actor_run(mock_actor_input, mock_push_data, mock_request_queue, httpx_mock):
    # Mock the HTTP responses
    httpx_mock.add_response(
        url="https://example.com",
        text='<html><head><title>Example</title></head><body>Example content</body></html>'
    )
    
    # Run the actor
    await run_apify_actor()
    
    # Since we've mocked all the Apify SDK calls, we just verify it completed without errors
    # In a real test environment, we would verify the data was pushed to the dataset