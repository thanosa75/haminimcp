import json
from datetime import datetime, timezone
from mcp.types import ToolAnnotations
from fastmcp import Context
from homeassistant_mcp.server import mcp
from homeassistant_mcp.models import (
    GetCalendarEventsInput,
    GetTodayEventsInput,
    CalendarEvent,
)
from homeassistant_mcp.ha_client import call_ha_api, is_error_response
from homeassistant_mcp.logger import get_logger

logger = get_logger(__name__)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def ha_list_calendars(ctx: Context) -> str:
    """List all available calendar entities in Home Assistant."""
    client = ctx.lifespan_context["client"]
    result = await call_ha_api(client, "GET", "/api/states", ctx)

    if is_error_response(result):
        return json.dumps(result)

    calendars_list = []
    # result is expected to be a list of entity states
    if isinstance(result, list):
        for entity in result:
            entity_id = entity.get("entity_id", "")
            if entity_id.startswith("calendar."):
                attributes = entity.get("attributes", {})
                calendars_list.append(
                    {
                        "entity_id": entity_id,
                        "state": entity.get("state"),
                        "name": attributes.get("friendly_name", entity_id),
                    }
                )

    logger.info(f"Listing all calendars, found {len(calendars_list)} calendar(s)")
    return json.dumps(calendars_list)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def ha_get_calendar_events(input: GetCalendarEventsInput, ctx: Context) -> str:
    """Get events for a specific calendar within a date range."""
    client = ctx.lifespan_context["client"]
    # Pydantic model GetCalendarEventsInput handles validation of start/end/90-day limit
    params = {"start": input.start, "end": input.end}
    result = await call_ha_api(
        client, "GET", f"/api/calendars/{input.entity_id}", ctx, params=params
    )

    if is_error_response(result):
        return json.dumps(result)

    events_list = []
    if isinstance(result, list):
        for event_data in result:
            try:
                # CalendarEvent model handles the actual structure
                event = CalendarEvent(**event_data)
                events_list.append(event.model_dump())
            except Exception as e:
                logger.error(f"Failed to parse calendar event: {e}. Data: {event_data}", exc_info=True)
                await ctx.error(f"Failed to parse calendar event: {e}. Data: {event_data}")
                continue

    logger.info(f"Fetching calendar events for {input.entity_id} from {input.start} to {input.end}, found {len(events_list)} event(s)")
    return json.dumps(events_list)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def ha_get_today_events(input: GetTodayEventsInput, ctx: Context) -> str:
    """Get all events scheduled for today across one or more calendars."""
    client = ctx.lifespan_context["client"]

    # Compute today's range in UTC
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    end = now.replace(
        hour=23, minute=59, second=59, microsecond=999999
    ).isoformat()

    # Determine which calendars to query
    calendar_ids = input.calendar_entity_ids
    if not calendar_ids:
        # Fetch all calendars if none specified
        states = await call_ha_api(client, "GET", "/api/states", ctx)
        if is_error_response(states):
            return json.dumps(states)

        calendar_ids = []
        if isinstance(states, list):
            for entity in states:
                eid = entity.get("entity_id", "")
                if eid.startswith("calendar."):
                    calendar_ids.append(eid)

    logger.info(f"Fetching today's events, querying {len(calendar_ids)} calendar(s): {calendar_ids}")
    
    all_results = {}
    for entity_id in calendar_ids:
        res = await call_ha_api(
            client, "GET", f"/api/calendars/{entity_id}", ctx, params={"start": start, "end": end}
        )
        
        if is_error_response(res):
            logger.error(f"Error fetching events for {entity_id}: {res}")
            await ctx.error(f"Error fetching events for {entity_id}: {res}")
            continue
            
        events_for_cal = []
        if isinstance(res, list):
            for event_data in res:
                try:
                    event = CalendarEvent(**event_data)
                    events_for_cal.append(event.model_dump())
                except Exception as e:
                    logger.error(f"Failed to parse event for {entity_id}: {e}", exc_info=True)
                    await ctx.error(f"Failed to parse event for {entity_id}: {e}")
                    continue
        
        logger.debug(f"Today's events for {entity_id}: {len(events_for_cal)} event(s)")
        all_results[entity_id] = events_for_cal

    logger.info(f"Today's events query complete, total {sum(len(v) for v in all_results.values())} event(s)")
    return json.dumps(all_results)
