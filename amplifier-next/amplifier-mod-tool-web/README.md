# Amplifier Web Tools Module

Web tools for searching and fetching content from the internet.

## Features

### WebSearchTool
- **Real web search** using DuckDuckGo (no API key required)
- Automatic fallback to mock results if search fails
- Configurable max results
- Returns structured results with title, URL, and snippet

### WebFetchTool
- Fetch and parse web pages
- Extract text from HTML content
- Domain allowlist/blocklist support
- Content size limits and timeout protection

## Installation

```bash
pip install -e .
```

## Usage

### Web Search

```python
from amplifier_mod_tool_web import WebSearchTool

# Create tool with config
tool = WebSearchTool({"max_results": 5})

# Execute search
result = await tool.execute({"query": "Python programming"})

# Results include:
# - title: Page title
# - url: Page URL
# - snippet: Brief description
```

### Web Fetch

```python
from amplifier_mod_tool_web import WebFetchTool

# Create tool with config
tool = WebFetchTool({
    "timeout": 10,
    "extract_text": True
})

# Fetch a webpage
result = await tool.execute({"url": "https://example.com"})

# Result includes extracted text content
```

## Configuration

- `max_results`: Maximum search results to return (default: 5)
- `timeout`: Request timeout in seconds (default: 10)
- `max_size`: Maximum content size in bytes (default: 1MB)
- `extract_text`: Extract text from HTML (default: True)
- `allowed_domains`: List of allowed domains (empty = all allowed)
- `blocked_domains`: List of blocked domains (includes localhost by default)

## Dependencies

- `ddgs`: DuckDuckGo search (no API key required)
- `aiohttp`: Async HTTP client
- `beautifulsoup4`: HTML parsing and text extraction
- `amplifier-core`: Core amplifier functionality