import json
from mcp.types import ToolAnnotations
from fastmcp import Context
from homeassistant_mcp.server import mcp
from homeassistant_mcp.models import GetLightInput, OperateLightInput, SetLightBrightnessInput
from homeassistant_mcp.ha_client import call_ha_api, is_error_response
from homeassistant_mcp.logger import get_logger
import httpx

logger = get_logger(__name__)

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def ha_list_lights(ctx: Context) -> str:
    """List all available light entities and their current states."""
    client = ctx.lifespan_context["client"]
    result = await call_ha_api(client, "GET", "/api/states", ctx)
    
    if is_error_response(result):
        return json.dumps(result)
    
    if not isinstance(result, list):
        return json.dumps({"error": "Unexpected response format from Home Assistant", "details": str(result)})

    lights_list = []
    for entity in result:
        entity_id = entity.get("entity_id", "")
        if entity_id.startswith("light."):
            attributes = entity.get("attributes", {})
            lights_list.append({
                "entity_id": entity_id,
                "state": entity.get("state"),
                "brightness": attributes.get("brightness"),
                "color_temp_kelvin": attributes.get("color_temp_kelvin"),
                "rgb_color": attributes.get("rgb_color"),
                "supported_color_modes": attributes.get("supported_color_modes", []),
                "friendly_name": attributes.get("friendly_name")
            })
            
    logger.info(f"Listing all lights, found {len(lights_list)} light(s)")
    return json.dumps(lights_list)

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def ha_get_light(input: GetLightInput, ctx: Context) -> str:
    """Get the current state and attributes of a specific light entity."""
    logger.info(f"Getting light state for {input.entity_id}")
    client = ctx.lifespan_context["client"]
    result = await call_ha_api(client, "GET", f"/api/states/{input.entity_id}", ctx)
    
    if is_error_response(result):
        return json.dumps(result)
        
    attributes = result.get("attributes", {})
    light_dict = {
        "entity_id": result.get("entity_id"),
        "state": result.get("state"),
        "brightness": attributes.get("brightness"),
        "color_temp_kelvin": attributes.get("color_temp_kelvin"),
        "rgb_color": attributes.get("rgb_color"),
        "supported_color_modes": attributes.get("supported_color_modes", []),
        "friendly_name": attributes.get("friendly_name")
    }
    
    return json.dumps(light_dict)

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False))
async def ha_operate_light(input: OperateLightInput, ctx: Context) -> str:
    """Turn a light on/off or toggle it with optional parameters like brightness and color."""
    logger.info(f"Operating light {input.entity_id}: action={input.action}, brightness={input.brightness}, color_temp={input.color_temp_kelvin}, rgb={input.rgb_color}")
    client = ctx.lifespan_context["client"]
    service_data = {"entity_id": input.entity_id}
    
    if input.brightness is not None:
        service_data["brightness"] = input.brightness
    if input.color_temp_kelvin is not None:
        service_data["color_temp_kelvin"] = input.color_temp_kelvin
    if input.rgb_color is not None:
        # Pydantic model ensures this is a tuple/list of 3 ints
        service_data["rgb_color"] = list(input.rgb_color)
    if input.transition is not None:
        service_data["transition"] = input.transition
        
    path = f"/api/services/light/{input.action}"
    result = await call_ha_api(client, "POST", path, ctx, json_body=service_data)
    
    if not is_error_response(result):
        return json.dumps({
            "success": True, 
            "action": input.action, 
            "entity_id": input.entity_id
        })
    
    return json.dumps(result)

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True))
async def ha_set_light_brightness(input: SetLightBrightnessInput, ctx: Context) -> str:
    """Set a light's brightness to a specific percentage (0-100)."""
    # MFR Bug Trap: round(pct / 100 * 255) and clamp to 0-255
    brightness_value = round(input.brightness_pct / 100 * 255)
    brightness_value = min(255, max(0, brightness_value))
    
    logger.info(f"Setting brightness for {input.entity_id} to {input.brightness_pct}% (raw: {brightness_value})")
    client = ctx.lifespan_context["client"]
    
    if brightness_value == 0:
        path = "/api/services/light/turn_off"
        service_data = {"entity_id": input.entity_id}
    else:
        path = "/api/services/light/turn_on"
        service_data = {"entity_id": input.entity_id, "brightness": brightness_value}
        
    result = await call_ha_api(client, "POST", path, ctx, json_body=service_data)
    
    if not is_error_response(result):
        return json.dumps({
            "success": True, 
            "entity_id": input.entity_id, 
            "brightness_pct": input.brightness_pct, 
            "brightness_raw": brightness_value
        })
        
    return json.dumps(result)
