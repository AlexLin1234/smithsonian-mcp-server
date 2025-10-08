# Smithsonian MCP Server

A Model Context Protocol (MCP) server that provides access to the Smithsonian Institution's Open Access API. Search and explore millions of items from the Smithsonian's collections including artifacts, artworks, specimens, photographs, and more.

## Features

- **Search Collections**: Search across millions of items from 19 Smithsonian museums and research centers
- **Get Item Details**: Retrieve comprehensive metadata about specific items
- **Browse Categories**: Discover available terms and filters for refining searches
- **Online Media**: Filter for items with images and other online media

## Installation

### Prerequisites

- Python 3.10 or higher
- A Smithsonian API key (free) - Get one at https://api.data.gov/signup/

### Setup

1. Clone the repository:
```bash
git clone https://github.com/AlexLin1234/smithsonian-mcp-server.git
cd smithsonian-mcp-server
```

2. Install the package:
```bash
pip install -e .
```

3. Set up your API key:
```bash
cp .env.example .env
# Edit .env and add your API key
```

Or set the environment variable directly:
```bash
export SMITHSONIAN_API_KEY=your_api_key_here
```

## Configuration for Claude Desktop

Add this to your Claude Desktop configuration file:

### MacOS
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows
Location: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "smithsonian": {
      "command": "python",
      "args": [
        "-m",
        "smithsonian_mcp_server.server"
      ],
      "env": {
        "SMITHSONIAN_API_KEY": "api-key-here"
      }
    }
  }
}
```

Alternatively, if you installed it in a virtual environment:

```json
{
  "mcpServers": {
    "smithsonian": {
      "command": "/path/to/venv/bin/python",
      "args": [
        "-m",
        "smithsonian_mcp_server.server"
      ],
      "env": {
        "SMITHSONIAN_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Available Tools

### search_collection

Search the Smithsonian collections with flexible query options.

**Parameters:**
- `query` (required): Search query string (supports keywords, phrases in quotes, AND/OR operators)
- `rows` (optional): Number of results to return (default: 10, max: 1000)
- `start` (optional): Starting offset for pagination (default: 0)
- `online_media_only` (optional): Only return items with online media/images (default: false)

**Example:**
```
Search for "space shuttle" items with images
```

### get_item

Get detailed information about a specific item.

**Parameters:**
- `item_id` (required): The Smithsonian item ID (obtained from search results)

**Example:**
```
Get details for item "edanmdm-NASM_A19600093000"
```

### get_category_terms

Get available terms for a specific category or facet.

**Parameters:**
- `category` (required): Category name (e.g., 'online_media_type', 'data_source', 'topic', 'place')
- `starts_with` (optional): Filter terms that start with this string

**Example:**
```
Get available topics starting with "Art"
```

## Example Usage

Once configured in Claude Desktop, you can ask Claude questions like:

- "Search the Smithsonian for information about the Wright Brothers"
- "Find items related to ancient Egypt with images"
- "Show me artifacts from the Air and Space Museum"
- "Get details about item edanmdm-NASM_A19600093000"
- "What data sources are available in the Smithsonian API?"

## API Information

This server uses the Smithsonian Open Access API v1.0:
- Base URL: `https://api.si.edu/openaccess/api/v1.0`
- Documentation: https://www.si.edu/openaccess/devtools
- Collections: 2.8+ million open access items
- Coverage: 19 Smithsonian museums, research centers, and libraries

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
ruff check src/
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues related to:
- This MCP server: Open an issue on GitHub
- The Smithsonian API: Visit https://www.si.edu/openaccess/faq
- Claude Desktop: Visit https://docs.claude.com
