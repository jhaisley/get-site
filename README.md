# Website to Markdown Crawler

An asynchronous web crawler that mirrors websites into a single organized markdown file, with special handling for images and proper directory structure preservation. Built with Python, asyncio, and httpx.

**Author**: Jordan Haisley (jordan@b-w.pro)

## Features

- 🚀 Fast asynchronous crawling using `httpx` and `asyncio`
- 📁 Preserves site structure - can be limited to specific subdirectories
- 🖼️ Smart image handling - preserves both alt text and filenames
- 📝 Clean Markdown output with proper sectioning
- 🔍 Depth-controlled crawling
- 🔒 Domain-restricted recursive crawling for safety
- 🤫 Quiet mode for silent operation

### As an Apify Actor

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