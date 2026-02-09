"""Support for Aldes text entities."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.const import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, FRIENDLY_NAMES, MANUFACTURER
from .entity import AldesEntity, DeviceContext

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from custom_components.aldes.coordinator import AldesDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add Aldes text entities from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    text_entities = []

    for device_key, device in (coordinator.data or {}).items():
        if not device:
            continue
        context = DeviceContext(
            device_key=device_key,
            device=device,
            config_entry=entry,
        )

        # Add planning entities if AquaAir reference
        if device.reference == "TONE_AQUA_AIR":
            # Heating programs
            text_entities.append(
                AldesPlanningEntity(
                    coordinator,
                    context,
                    planning_type="heating_prog_a",
                    planning_key="week_planning",
                )
            )
            text_entities.append(
                AldesPlanningEntity(
                    coordinator,
                    context,
                    planning_type="heating_prog_b",
                    planning_key="week_planning2",
                )
            )
            # Cooling programs
            text_entities.append(
                AldesPlanningEntity(
                    coordinator,
                    context,
                    planning_type="cooling_prog_c",
                    planning_key="week_planning3",
                )
            )
            text_entities.append(
                AldesPlanningEntity(
                    coordinator,
                    context,
                    planning_type="cooling_prog_d",
                    planning_key="week_planning4",
                )
            )

    async_add_entities(text_entities)


class AldesPlanningEntity(AldesEntity, Entity):
    """Representation of the weekly planning as a diagnostic entity."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_visible_default = False

    def __init__(
        self,
        coordinator: AldesDataUpdateCoordinator,
        context: DeviceContext,
        planning_type: str,
        planning_key: str,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, context)
        self.planning_type = planning_type
        self.planning_key = planning_key

    @property
    def state(self) -> str:
        """Return a short state."""
        device = self._get_device()
        if not device:
            return "unavailable"

        try:
            planning = getattr(device, self.planning_key, None)
        except Exception:
            _LOGGER.exception("Error getting planning state %s", self.planning_type)
            return "error"
        else:
            if planning and isinstance(planning, list):
                return f"{len(planning)} items"
            return "unknown"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes with planning data."""
        device = self._get_device()
        if not device:
            return {}

        try:
            planning = getattr(device, self.planning_key, None)
        except Exception:
            _LOGGER.exception(
                "Error getting planning attributes %s", self.planning_type
            )
            return {}
        else:
            if not planning:
                return {}
            commands = [
                item if isinstance(item, str) else item.get("command")
                for item in planning
                if isinstance(item, str | dict)
            ]
            commands = [c for c in commands if c]
            return {
                "planning_data": commands,
                "planning_json": json.dumps(commands, indent=2),
                "item_count": len(commands),
            }

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.serial_number)},
            manufacturer=MANUFACTURER,
            name=f"{FRIENDLY_NAMES[self.reference]} {self.serial_number}",
            model=FRIENDLY_NAMES[self.reference],
        )

    @property
    def unique_id(self) -> str | None:
        """Return a unique ID to use for this entity."""
        return f"{self.serial_number}_planning_{self.planning_type}"

    @property
    def icon(self) -> str:
        """Return the icon."""
        if "heating" in self.planning_type:
            return "mdi:fire"
        if "cooling" in self.planning_type:
            return "mdi:snowflake"
        return "mdi:calendar-week"

    def _friendly_name_internal(self) -> str | None:
        """Return the friendly name."""
        names = {
            "heating_prog_a": "Planning Chauffage Programme A",
            "heating_prog_b": "Planning Chauffage Programme B",
            "cooling_prog_c": "Planning Climatisation Programme C",
            "cooling_prog_d": "Planning Climatisation Programme D",
        }
        return names.get(self.planning_type, "Planning")

    @property
    def native_value(self) -> str:
        """Return the current planning as JSON string."""
        device = self._get_device()
        if not device:
            return "{}"

        try:
            planning = getattr(device, self.planning_key, None)
        except Exception:
            _LOGGER.exception("Error formatting planning %s", self.planning_type)
            return "{}"
        else:
            if not planning:
                return "{}"
            commands = [
                item if isinstance(item, str) else item.get("command")
                for item in planning
                if isinstance(item, str | dict)
            ]
            commands = [c for c in commands if c]
            return json.dumps(commands, indent=2)

    async def async_set_native_value(self, value: str) -> None:
        """Set planning value."""
        try:
            # Parse JSON to validate
            planning = json.loads(value)

            # Validate structure
            if not isinstance(planning, list):
                _LOGGER.error("Planning must be a JSON array")
                return

            # Validate each command
            for item in planning:
                if not isinstance(item, dict) or "command" not in item:
                    _LOGGER.error("Each planning item must have a 'command' field")
                    return

            _LOGGER.info(
                "Planning %s updated: %d items", self.planning_type, len(planning)
            )
            # Update the device data
            device = self._get_device()
            if device:
                setattr(device, self.planning_key, planning)
            self.async_write_ha_state()

        except json.JSONDecodeError:
            _LOGGER.exception("Invalid JSON in planning")
        except Exception:
            _LOGGER.exception("Error setting planning")
