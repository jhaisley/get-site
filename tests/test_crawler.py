import pytest
from pathlib import Path
from bs4 import BeautifulSoup
from src.main import AsyncWebCrawler, parse_args
import sys

@pytest.fixture
def test_html():
    return """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <img src="/images/test.jpg" alt="Test Image">
            <a href="/page1">Link 1</a>
            <a href="https://example.com/page2">External Link</a>
            <a href="/docs/page3">Docs Link</a>
            <div>Some content</div>
        </body>
    </html>
    """

@pytest.fixture
def mock_httpx_client(httpx_mock):
    # Mock the main page
    httpx_mock.add_response(
        url="https://example.com",
        text="""<html><head><title>Main Page</title></head>
        <body><a href="/page1">Link 1</a></body></html>"""
    )
    # Mock the linked page
    httpx_mock.add_response(
        url="https://example.com/page1",
        text='<html><head><title>Page 1</title></head><body>Page 1 content</body></html>'
    )
    return httpx_mock

@pytest.mark.asyncio
async def test_crawler_initialization():
    crawler = AsyncWebCrawler("https://example.com")
    assert crawler.base_url == "https://example.com"
    assert crawler.domain == "example.com"
    assert crawler.base_path == ""
    
    # Test with subdirectory
    crawler = AsyncWebCrawler("https://example.com/docs/")
    assert crawler.base_path == "/docs"

@pytest.mark.asyncio
async def test_is_valid_url():
    crawler = AsyncWebCrawler("https://example.com/docs/")
    
    # Valid URLs
    assert crawler.is_valid_url("https://example.com/docs/page1")
    assert crawler.is_valid_url("https://example.com/docs/nested/page2")
    
    # Invalid URLs
    assert not crawler.is_valid_url("https://example.com/blog")  # Outside base path
    assert not crawler.is_valid_url("https://other-domain.com/docs/page")  # Wrong domain
    assert not crawler.is_valid_url("https://example.com/docs/image.jpg")  # Binary file

def test_process_images(test_html):
    crawler = AsyncWebCrawler("https://example.com")
    soup = BeautifulSoup(test_html, 'html.parser')
    markdown_images = crawler.process_images(soup, "https://example.com")
    assert "![Test Image (File: test.jpg)](https://example.com/images/test.jpg)" in markdown_images

@pytest.mark.asyncio
async def test_crawl_page(async_client, mock_httpx_client):
    crawler = AsyncWebCrawler("https://example.com", max_depth=1)
    await crawler.crawl_page(async_client, "https://example.com", 0)
    
    # Check that both pages were visited
    assert "https://example.com" in crawler.visited
    assert "https://example.com/page1" in crawler.visited
    assert len(crawler.visited) == 2
    
    # Check that both pages were processed
    assert len(crawler.content) == 2
    assert any(page['title'] == 'Main Page' for page in crawler.content)
    assert any(page['title'] == 'Page 1' for page in crawler.content)

@pytest.mark.asyncio
async def test_quiet_mode(async_client, capsys):
    response_text = """<html><head><title>Test Page</title></head><body>Test content</body></html>"""
    
    # Test with quiet mode off (default)
    with pytest.MonkeyPatch.context() as mp:
        crawler = AsyncWebCrawler("https://example.com", quiet=False)
        async def mock_get(*args, **kwargs):
            class MockResponse:
                text = response_text
                def raise_for_status(self): pass
            return MockResponse()
        mp.setattr(async_client, "get", mock_get)
        
        await crawler.crawl_page(async_client, "https://example.com", 0)
        captured = capsys.readouterr()
        assert "Crawling: https://example.com" in captured.out
    
    # Test with quiet mode on
    with pytest.MonkeyPatch.context() as mp:
        crawler = AsyncWebCrawler("https://example.com", quiet=True)
        async def mock_get(*args, **kwargs):
            class MockResponse:
                text = response_text
                def raise_for_status(self): pass
            return MockResponse()
        mp.setattr(async_client, "get", mock_get)
        
        await crawler.crawl_page(async_client, "https://example.com", 0)
        captured = capsys.readouterr()
        assert captured.out == ""

@pytest.mark.asyncio
async def test_save_markdown_output_modes(async_client, mock_httpx_client, tmp_path):
    crawler = AsyncWebCrawler("https://example.com")
    await crawler.crawl_page(async_client, "https://example.com", 0)
    
    # Test returning content as string
    content = crawler.save_markdown()
    assert isinstance(content, str)
    assert "Main Page" in content
    
    # Test saving to file
    output_file = tmp_path / "test.md"
    returned_content = crawler.save_markdown(output_file)
    assert output_file.exists()
    assert returned_content == content  # Should return same content whether saving or not

def test_argument_parsing():
    # Test URL argument
    sys.argv = ['script.py', 'https://example.com']
    args = parse_args()
    assert args.url == 'https://example.com'
    assert not args.quiet
    assert args.max_depth == 1
    assert args.output is None
    
    # Test all arguments
    sys.argv = ['script.py', 'https://example.com', '-q', '-o', 'output.md', '-d', '2']
    args = parse_args()
    assert args.url == 'https://example.com'
    assert args.quiet
    assert args.max_depth == 2
    assert args.output == 'output.md'