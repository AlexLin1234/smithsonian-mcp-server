"""Quick test script to verify the Smithsonian API connection."""

import asyncio
import os
from dotenv import load_dotenv
from smithsonian_mcp_server.server import search_smithsonian, get_item_details

# Load environment variables from .env.example
load_dotenv(".env.example")


async def test_search():
    """Test the search functionality."""
    print("Testing Smithsonian API search...")
    print("-" * 50)

    try:
        # Test a simple search
        results = await search_smithsonian(
            query="apollo 11",
            rows=5,
            online_media=True
        )

        print(f"[OK] Search successful!")
        print(f"  Found {results.get('response', {}).get('rowCount', 0)} results")

        # Show first result
        rows = results.get('response', {}).get('rows', [])
        if rows:
            first_item = rows[0]
            print(f"\n  First result:")
            print(f"    Title: {first_item.get('title', 'N/A')}")
            print(f"    ID: {first_item.get('id', 'N/A')}")

            return first_item.get('id')

    except Exception as e:
        print(f"[FAIL] Search failed: {e}")
        return None


async def test_get_item(item_id):
    """Test getting item details."""
    if not item_id:
        print("\nSkipping item details test (no item ID)")
        return

    print(f"\nTesting item details for ID: {item_id}")
    print("-" * 50)

    try:
        details = await get_item_details(item_id)
        print(f"[OK] Item details retrieved successfully!")

        response = details.get('response', {})
        print(f"  Title: {response.get('title', 'N/A')}")
        print(f"  Unit: {response.get('unitCode', 'N/A')}")

    except Exception as e:
        print(f"[FAIL] Get item failed: {e}")


async def main():
    """Run all tests."""
    print("Smithsonian MCP Server API Test")
    print("=" * 50)

    # Check for API key
    api_key = os.getenv("SMITHSONIAN_API_KEY")
    if not api_key:
        print("[FAIL] Error: SMITHSONIAN_API_KEY environment variable not set")
        print("  Please set it in your .env file or environment")
        return

    print(f"[OK] API key found: {api_key[:10]}...")
    print()

    # Run tests
    item_id = await test_search()
    await test_get_item(item_id)

    print("\n" + "=" * 50)
    print("Tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
