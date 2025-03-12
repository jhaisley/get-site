# Website to Markdown Crawler

An asynchronous web crawler that mirrors websites into a single organized markdown file, with special handling for images and proper directory structure preservation. Built with Python, asyncio, and httpx.

**Author**: Jordan Haisley (jordanhaisley@gmail.com)

## Features

- 🚀 Fast asynchronous crawling using `httpx` and `asyncio`
- 📁 Preserves site structure - can be limited to specific subdirectories
- 🖼️ Smart image handling - preserves both alt text and filenames
- 📝 Clean Markdown output with proper sectioning
- 🔍 Depth-controlled crawling
- 🤖 Dual mode operation: CLI tool or Apify actor
- 🔒 Domain-restricted crawling for safety
- 🤫 Quiet mode for silent operation
- 📤 Flexible output options (file or terminal)

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

Basic usage with output to terminal:
```bash
uv run -m src https://example.com
```

Advanced usage with all options:
```bash
uv run -m src [URL] [-o OUTPUT_FILE] [-q] [-d MAX_DEPTH]
```

Options:
- `-o, --output`: Save output to specified file instead of terminal
- `-q, --quiet`: Suppress all output except errors
- `-d, --max-depth`: Maximum crawl depth (default: 1)

Examples:
```bash
# Crawl quietly and save to file
uv run -m src -q -o output.md https://example.com

# Crawl subdirectory with depth 2
uv run -m src -d 2 https://example.com/docs/

# Output to terminal silently
uv run -m src -q https://example.com
```

### As an Apify Actor

Run without arguments to use as an Apify actor:
```bash
uv run -m src
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

## Testing

Run the test suite using:
```bash
uv run -m pytest
```

For verbose output:
```bash
uv run -m pytest -v
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.