"""
Main Entry Point for Home Assistant MCP Server.

This module initializes the FastMCP server, triggers tool registrations 
by importing tool modules, and starts the server via stdio transport.
"""

from homeassistant_mcp.logger import setup_logging, get_logger

# Initialize logging before other imports if possible,
# but we need to ensure the logger is ready for the modules we import below.
logger = setup_logging()

import homeassistant_mcp.light_tools  # noqa: F401
import homeassistant_mcp.calendar_tools  # noqa: F401
from homeassistant_mcp.server import mcp


def main() -> None:
    """Run the FastMCP server."""
    logger.info("Home Assistant MCP Server starting")
    try:
        mcp.run()
    except Exception as e:
        logger.error(f"Home Assistant MCP Server encountered an error: {e}", exc_info=True)
    finally:
        logger.info("Home Assistant MCP Server shutting down")


if __name__ == "__main__":
    main()
