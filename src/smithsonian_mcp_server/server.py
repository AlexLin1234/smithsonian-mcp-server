"""
Smithsonian MCP Server

An MCP server that provides access to the Smithsonian Institution's Open Access API,
allowing users to search and retrieve information about millions of items from the
Smithsonian collections.
"""

import os
import asyncio
from typing import Any, Optional
import httpx
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from pydantic import AnyUrl
import mcp.server.stdio


# API configuration
SMITHSONIAN_API_BASE = "https://api.si.edu/openaccess/api/v1.0"
DEFAULT_API_KEY = os.getenv("SMITHSONIAN_API_KEY", "")


app = Server("smithsonian-mcp-server")


def get_api_key() -> str:
    """Get the Smithsonian API key from environment variable."""
    api_key = os.getenv("SMITHSONIAN_API_KEY", DEFAULT_API_KEY)
    if not api_key:
        raise ValueError(
            "SMITHSONIAN_API_KEY environment variable is required. "
            "Get your free API key at https://api.data.gov/signup/"
        )
    return api_key


async def search_smithsonian(
    query: str,
    rows: int = 10,
    start: int = 0,
    online_media: bool = False,
) -> dict[str, Any]:
    """
    Search the Smithsonian collections.

    Args:
        query: Search query string
        rows: Number of results to return (default 10, max 1000)
        start: Starting offset for pagination (default 0)
        online_media: Only return items with online media (default False)

    Returns:
        Dictionary containing search results
    """
    api_key = get_api_key()

    params = {
        "api_key": api_key,
        "q": query,
        "rows": min(rows, 1000),
        "start": start,
    }

    if online_media:
        params["online_media_type"] = "Images"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{SMITHSONIAN_API_BASE}/search",
            params=params,
        )
        response.raise_for_status()
        return response.json()


async def get_item_details(item_id: str) -> dict[str, Any]:
    """
    Get detailed information about a specific item.

    Args:
        item_id: The Smithsonian item ID

    Returns:
        Dictionary containing item details
    """
    api_key = get_api_key()

    params = {"api_key": api_key}

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{SMITHSONIAN_API_BASE}/content/{item_id}",
            params=params,
        )
        response.raise_for_status()
        return response.json()


async def get_category_terms(category: str, starts_with: str = "") -> dict[str, Any]:
    """
    Get available terms for a specific category/facet.

    Args:
        category: Category name (e.g., 'online_media_type', 'data_source', 'topic', 'place')
        starts_with: Filter terms that start with this string

    Returns:
        Dictionary containing available terms
    """
    api_key = get_api_key()

    params = {
        "api_key": api_key,
        "category": category,
    }

    if starts_with:
        params["starts_with"] = starts_with

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{SMITHSONIAN_API_BASE}/terms/{category}",
            params=params,
        )
        response.raise_for_status()
        return response.json()


def format_search_results(data: dict[str, Any]) -> str:
    """Format search results into a readable text format."""
    response = data.get("response", {})
    rows_returned = response.get("rowCount", 0)
    total_rows = response.get("rowCount", 0)

    result_lines = [
        f"Found {total_rows} results",
        f"Showing {rows_returned} items:",
        "",
    ]

    for item in response.get("rows", []):
        title = item.get("title", "Untitled")
        item_id = item.get("id", "Unknown ID")
        unit_code = item.get("unitCode", "")

        result_lines.append(f"• {title}")
        result_lines.append(f"  ID: {item_id}")

        if unit_code:
            result_lines.append(f"  Unit: {unit_code}")

        # Add content description if available
        content = item.get("content", {})
        if isinstance(content, dict):
            desc = content.get("descriptiveNonRepeating", {})
            if isinstance(desc, dict):
                record_link = desc.get("record_link")
                if record_link:
                    result_lines.append(f"  Link: {record_link}")

        # Check for online media
        online_media = item.get("content", {}).get("descriptiveNonRepeating", {}).get("online_media", {})
        if online_media and isinstance(online_media, dict):
            media_count = online_media.get("mediaCount", 0)
            if media_count > 0:
                result_lines.append(f"  Online Media: {media_count} items available")

        result_lines.append("")

    return "\n".join(result_lines)


def format_item_details(data: dict[str, Any]) -> str:
    """Format item details into a readable text format."""
    response = data.get("response", {})

    result_lines = ["Item Details:", ""]

    # Basic info
    title = response.get("title", "Untitled")
    item_id = response.get("id", "Unknown")
    unit_code = response.get("unitCode", "")

    result_lines.append(f"Title: {title}")
    result_lines.append(f"ID: {item_id}")

    if unit_code:
        result_lines.append(f"Unit: {unit_code}")

    result_lines.append("")

    # Content details
    content = response.get("content", {})
    if isinstance(content, dict):
        # Descriptive info
        desc = content.get("descriptiveNonRepeating", {})
        if isinstance(desc, dict):
            record_link = desc.get("record_link")
            if record_link:
                result_lines.append(f"Record Link: {record_link}")

            # Data source
            data_source = desc.get("data_source")
            if data_source:
                result_lines.append(f"Data Source: {data_source}")

            # Online media
            online_media = desc.get("online_media", {})
            if online_media and isinstance(online_media, dict):
                result_lines.append("")
                result_lines.append("Online Media:")
                media_count = online_media.get("mediaCount", 0)
                result_lines.append(f"  Total Items: {media_count}")

                # List media items
                for media in online_media.get("media", [])[:5]:  # Show first 5
                    if isinstance(media, dict):
                        media_type = media.get("type", "Unknown")
                        media_url = media.get("content", "")
                        result_lines.append(f"  - {media_type}: {media_url}")

        # Free text fields
        freetext = content.get("freetext", {})
        if isinstance(freetext, dict):
            result_lines.append("")
            result_lines.append("Additional Information:")

            for key, values in freetext.items():
                if isinstance(values, list) and values:
                    result_lines.append(f"  {key}:")
                    for item in values[:3]:  # Show first 3
                        if isinstance(item, dict):
                            label = item.get("label", "")
                            content_text = item.get("content", "")
                            if label:
                                result_lines.append(f"    {label}: {content_text}")
                            else:
                                result_lines.append(f"    {content_text}")

    return "\n".join(result_lines)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="search_collection",
            description=(
                "Search the Smithsonian Institution's collections. "
                "Search across millions of items including artifacts, artworks, specimens, and more. "
                "Returns a list of matching items with basic information."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (supports keywords, phrases in quotes, AND/OR operators)",
                    },
                    "rows": {
                        "type": "number",
                        "description": "Number of results to return (default 10, max 1000)",
                        "default": 10,
                    },
                    "start": {
                        "type": "number",
                        "description": "Starting offset for pagination (default 0)",
                        "default": 0,
                    },
                    "online_media_only": {
                        "type": "boolean",
                        "description": "Only return items that have online media/images available",
                        "default": False,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_item",
            description=(
                "Get detailed information about a specific Smithsonian collection item. "
                "Provides comprehensive metadata including descriptions, dates, creators, "
                "physical details, and links to online media if available."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "item_id": {
                        "type": "string",
                        "description": "The Smithsonian item ID (obtained from search results)",
                    },
                },
                "required": ["item_id"],
            },
        ),
        Tool(
            name="get_category_terms",
            description=(
                "Get available terms/values for a specific category or facet. "
                "Useful for discovering valid filter values. "
                "Categories include: online_media_type, data_source, topic, place, and more."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Category name (e.g., 'online_media_type', 'data_source', 'topic', 'place')",
                    },
                    "starts_with": {
                        "type": "string",
                        "description": "Optional: filter terms that start with this string",
                        "default": "",
                    },
                },
                "required": ["category"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "search_collection":
            query = arguments.get("query")
            rows = arguments.get("rows", 10)
            start = arguments.get("start", 0)
            online_media_only = arguments.get("online_media_only", False)

            if not query:
                return [TextContent(type="text", text="Error: query parameter is required")]

            data = await search_smithsonian(
                query=query,
                rows=rows,
                start=start,
                online_media=online_media_only,
            )

            formatted_result = format_search_results(data)
            return [TextContent(type="text", text=formatted_result)]

        elif name == "get_item":
            item_id = arguments.get("item_id")

            if not item_id:
                return [TextContent(type="text", text="Error: item_id parameter is required")]

            data = await get_item_details(item_id)
            formatted_result = format_item_details(data)
            return [TextContent(type="text", text=formatted_result)]

        elif name == "get_category_terms":
            category = arguments.get("category")
            starts_with = arguments.get("starts_with", "")

            if not category:
                return [TextContent(type="text", text="Error: category parameter is required")]

            data = await get_category_terms(category, starts_with)

            # Format the terms
            response = data.get("response", {})
            terms = response.get("terms", [])

            result_lines = [f"Available terms for '{category}':", ""]
            for term in terms:
                result_lines.append(f"• {term}")

            result_text = "\n".join(result_lines)
            return [TextContent(type="text", text=result_text)]

        else:
            return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
