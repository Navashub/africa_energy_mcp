"""
Africa Energy Data MCP Server
Wraps the Africa Energy Data API to expose tools for MCP clients (Claude, Cursor, etc.)

Usage:
    python server.py

Requirements:
    pip install mcp httpx python-dotenv
"""

import logging
import sys
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from config import SERVER_NAME, SERVER_VERSION
from tools import get_tools
from handlers import call_tool
from api_client import APIClient

# ── Logging Setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,  # Output to stderr so it doesn't interfere with MCP stdio
)
logger = logging.getLogger(__name__)

# ── MCP Server ─────────────────────────────────────────────────────────────────

server = Server(SERVER_NAME)
api_client = APIClient()


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Declare all tools the MCP server exposes."""
    logger.debug("list_tools called")
    return get_tools()


@server.call_tool()
async def handle_call_tool_impl(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    """Route tool calls to the handlers module."""
    async with APIClient() as client:
        return await call_tool(name, arguments, client)


# ── Entry Point ────────────────────────────────────────────────────────────────

async def main():
    logger.info(f"Starting {SERVER_NAME} v{SERVER_VERSION}")
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=SERVER_NAME,
                server_version=SERVER_VERSION,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())