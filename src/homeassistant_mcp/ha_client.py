import httpx
from fastmcp import Context
from homeassistant_mcp.logger import get_logger
from homeassistant_mcp.const import DEFAULT_TIMEOUT

logger = get_logger(__name__)

async def call_ha_api(client: httpx.AsyncClient, method: str, path: str, ctx: Context, *, json_body: dict | None = None, params: dict | None = None) -> dict | list:
    """Centralized async function for making Home Assistant API calls with proper error handling."""
    await ctx.info(f"HA API {method} {path}")
    logger.debug(f"Calling HA API: {method} {path} with params={params}")
    
    try:
        response = await client.request(
            method=method,
            url=path,
            json=json_body,
            params=params
        )
        response.raise_for_status()
        logger.debug(f"HA API {method} {path} returned status {response.status_code}")
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HA API {method} {path}: HTTP {e.response.status_code} - {e.response.text}")
        await ctx.error(f"HA API error: {e.response.status_code} - {e.response.text}")
        return {"error": f"HA API error: {e.response.status_code}", "detail": e.response.text}
    except httpx.TimeoutException as e:
        logger.error(f"HA API {method} {path}: Timeout after {DEFAULT_TIMEOUT}s")
        await ctx.error(f"HA API timeout: {str(e)}")
        return {"error": "HA API timeout", "detail": str(e)}
    except Exception as e:
        logger.error(f"HA API {method} {path}: Unexpected error - {type(e).__name__}: {str(e)}", exc_info=True)
        await ctx.error(f"Unexpected HA API error: {str(e)}")
        return {"error": "Unexpected error", "detail": str(e)}

def is_error_response(result: dict | list) -> bool:
    """Returns True if the result dictionary contains an 'error' key."""
    if isinstance(result, dict) and "error" in result:
        logger.debug(f"Error response detected in result: {result.get('error')}")
        return True
    return False
