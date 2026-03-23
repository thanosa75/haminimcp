from contextlib import asynccontextmanager
import os
import httpx
from fastmcp import FastMCP
from homeassistant_mcp.const import DEFAULT_TIMEOUT, ENV_HA_BASE_URL, ENV_HA_TOKEN
from homeassistant_mcp.logger import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(server: FastMCP):
    """
    Manages the lifecycle of the Home Assistant MCP Server.
    Creates an httpx.AsyncClient for communicating with the Home Assistant API.
    """
    logger.debug("Server lifespan: acquiring resources")
    
    # Let KeyError propagate if environment variables are missing
    try:
        base_url = os.environ[ENV_HA_BASE_URL].rstrip("/")
        token = os.environ[ENV_HA_TOKEN]
    except KeyError as e:
        logger.error(f"Missing environment variable: {e}")
        raise

    async with httpx.AsyncClient(
        base_url=base_url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        timeout=httpx.Timeout(DEFAULT_TIMEOUT),
    ) as client:
        logger.info(f"Home Assistant client initialized with base_url={base_url}")
        logger.debug("Server lifespan: resources ready")
        yield {"client": client}
    
    logger.info("Server lifespan: cleaning up resources")

# Create the FastMCP server instance
logger.info("Initializing FastMCP server instance")
mcp = FastMCP("Home Assistant", lifespan=lifespan)
