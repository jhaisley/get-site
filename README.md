# Website to Markdown Crawler

An asynchronous web crawler that mirrors websites into a single organized markdown file, with special handling for images and proper directory structure preservation. Built with Python, asyncio, and httpx.

## Features

- 🚀 Fast asynchronous crawling using `httpx` and `asyncio`
- 📁 Preserves site structure - can be limited to specific subdirectories
- 🖼️ Smart image handling - preserves both alt text and filenames
- 📝 Clean Markdown output with proper sectioning
- 🔍 Depth-controlled crawling
- 🤖 Dual mode operation: CLI tool or Apify actor
- 🔒 Domain-restricted crawling for safety

## Installation

### Prerequisites
- Python 3.13+
- uv (recommended) or pip

### Using uv (Recommended)
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies using uv
uv pip install -e .
```

### Using pip
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

## Usage

### As a CLI Tool

Basic usage to crawl an entire domain:
```bash
python main.py https://example.com
```

To crawl a specific subdirectory (will not crawl parent directory):
```bash
python main.py https://example.com/docs/
```

The crawler will:
1. Visit each page under the specified URL
2. Convert HTML content to Markdown
3. Process and include images with alt text and filenames
4. Save everything to `crawled_site.md`

### As an Apify Actor

Run without arguments to use as an Apify actor:
```bash
python main.py
```

Actor input schema:
```json
{
    "start_urls": [{"url": "https://example.com"}],
    "max_depth": 1
}
```

## Output Format

The generated markdown file contains:
- A section for each page
- Page title as heading
- Original URL reference
- Page content in Markdown format
- Image references with both alt text and filenames

Example output:
```markdown
# Page Title
*URL: https://example.com/page*

![Alt text (File: image.jpg)](https://example.com/image.jpg)

Page content in markdown...

----------------
```

## Dependencies

- `httpx` - Async HTTP client
- `beautifulsoup4` - HTML parsing
- `html2text` - HTML to Markdown conversion
- `validators` - URL validation
- `apify` - Apify platform integration (optional)

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.