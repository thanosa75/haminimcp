from __future__ import annotations
from typing import Literal
import dateutil.parser
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Strict config for all models except CalendarEvent
model_config_strict = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra='forbid')

class LightState(BaseModel):
    model_config = model_config_strict

    entity_id: str
    state: str
    brightness: int | None = None
    color_temp_kelvin: int | None = None
    rgb_color: tuple[int, int, int] | None = None
    supported_color_modes: list[str] = Field(default_factory=list)
    friendly_name: str | None = None

    @field_validator("entity_id")
    @classmethod
    def validate_light_entity_id(cls, v: str) -> str:
        if not v.startswith("light."):
            raise ValueError("entity_id must start with 'light.'")
        return v

class GetLightInput(BaseModel):
    model_config = model_config_strict

    entity_id: str

    @field_validator("entity_id")
    @classmethod
    def validate_light_entity_id(cls, v: str) -> str:
        if not v.startswith("light."):
            raise ValueError("entity_id must start with 'light.'")
        return v

class OperateLightInput(BaseModel):
    model_config = model_config_strict

    entity_id: str
    action: Literal["turn_on", "turn_off", "toggle"]
    brightness: int | None = Field(default=None, ge=0, le=255)
    color_temp_kelvin: int | None = Field(default=None, gt=0)
    rgb_color: tuple[int, int, int] | None = None
    transition: float | None = Field(default=None, ge=0)

    @field_validator("entity_id")
    @classmethod
    def validate_light_entity_id(cls, v: str) -> str:
        if not v.startswith("light."):
            raise ValueError("entity_id must start with 'light.'")
        return v

    @model_validator(mode="after")
    def validate_logic(self) -> OperateLightInput:
        # (a) Check action compatibility
        if self.action in ("turn_off", "toggle"):
            if any(x is not None for x in (self.brightness, self.color_temp_kelvin, self.rgb_color, self.transition)):
                raise ValueError(f"Cannot set light attributes when action is '{self.action}'; only turn_on supports attributes")
        
        # (b) Mutual exclusivity
        if self.color_temp_kelvin is not None and self.rgb_color is not None:
            raise ValueError("color_temp_kelvin and rgb_color are mutually exclusive")
            
        # (c) RGB bounds
        if self.rgb_color is not None:
            if not all(0 <= c <= 255 for c in self.rgb_color):
                raise ValueError("rgb_color components must be in range 0-255")
        
        return self

class SetLightBrightnessInput(BaseModel):
    model_config = model_config_strict

    entity_id: str
    brightness_pct: int = Field(ge=0, le=100)

    @field_validator("entity_id")
    @classmethod
    def validate_light_entity_id(cls, v: str) -> str:
        if not v.startswith("light."):
            raise ValueError("entity_id must start with 'light.'")
        return v

class CalendarInfo(BaseModel):
    model_config = model_config_strict

    entity_id: str
    name: str
    state: str

    @field_validator("entity_id")
    @classmethod
    def validate_calendar_entity_id(cls, v: str) -> str:
        if not v.startswith("calendar."):
            raise ValueError("entity_id must start with 'calendar.'")
        return v

class GetCalendarEventsInput(BaseModel):
    model_config = model_config_strict

    entity_id: str
    start: str
    end: str

    @field_validator("entity_id")
    @classmethod
    def validate_calendar_entity_id(cls, v: str) -> str:
        if not v.startswith("calendar."):
            raise ValueError("entity_id must start with 'calendar.'")
        return v

    @model_validator(mode="after")
    def validate_dates(self) -> GetCalendarEventsInput:
        try:
            start_dt = dateutil.parser.isoparse(self.start)
            end_dt = dateutil.parser.isoparse(self.end)
        except Exception as e:
            raise ValueError(f"Invalid ISO8601 date format: {e}")

        if start_dt >= end_dt:
            raise ValueError("start must be before end")
        
        if (end_dt - start_dt).days > 90:
            raise ValueError("Date range must not exceed 90 days")
            
        return self

class GetTodayEventsInput(BaseModel):
    model_config = model_config_strict

    calendar_entity_ids: list[str] | None = None

    @field_validator("calendar_entity_ids")
    @classmethod
    def validate_calendar_ids(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            for item in v:
                if not item.startswith("calendar."):
                    raise ValueError(f"calendar_entity_ids entry '{item}' must start with 'calendar.'")
        return v

class CalendarEvent(BaseModel):
    # Relaxed config for this model
    model_config = ConfigDict(str_strip_whitespace=True, extra='ignore')

    summary: str | None = None
    start: str | dict | None = None
    end: str | dict | None = None
    description: str | None = None
    location: str | None = None

    @field_validator("start", "end", mode="before")
    @classmethod
    def unwrap_ha_datetime(cls, v: str | dict | None) -> str | None:
        if isinstance(v, dict):
            return v.get("dateTime") or v.get("date")
        return v
