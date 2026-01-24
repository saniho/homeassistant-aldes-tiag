"""Diagnostics support for Aldes integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    api = coordinator.api
    data = coordinator.data

    if data is None:
        return {
            "error": "No data available from coordinator",
            "coordinator_status": "error",
        }

    # Build diagnostics dictionary
    diagnostics: dict[str, Any] = {
        "coordinator_status": "ok",
        "last_update": coordinator.last_update_success,
        "update_interval": str(coordinator.update_interval),
        "device": {
            "reference": data.reference,
            "type": data.type,
            "serial_number": data.serial_number,
            "modem": data.modem,
            "is_connected": data.is_connected,
            "has_filter": data.has_filter,
            "filter_wear": data.filter_wear,
            "last_updated_date": data.last_updated_date,
            "date_last_filter_update": data.date_last_filter_update,
        },
        "indicator": {
            "main_temperature": data.indicator.main_temperature,
            "current_air_mode": str(data.indicator.current_air_mode),
            "current_water_mode": str(data.indicator.current_water_mode),
            "hot_water_quantity": data.indicator.hot_water_quantity,
            "temperature_limits": {
                "heating_min": data.indicator.fmist,
                "heating_max": data.indicator.fmast,
                "cooling_min": data.indicator.cmist,
                "cooling_max": data.indicator.cmast,
            },
            "holidays": {
                "start_date": data.holidays_start,
                "end_date": data.holidays_end,
                "frost_protection_enabled": data.hors_gel,
            },
        },
        "thermostats": [
            {
                "id": t.id,
                "name": t.name,
                "number": t.number,
                "current_temperature": t.current_temperature,
                "temperature_set": t.temperature_set,
            }
            for t in data.indicator.thermostats
        ],
        "settings": {
            "household_composition": (
                str(data.indicator.settings.people)
                if data.indicator.settings.people
                else None
            ),
            "antilegio_cycle": data.indicator.settings.antilegio,
            "kwh_creuse": data.indicator.settings.kwh_creuse,
            "kwh_pleine": data.indicator.settings.kwh_pleine,
        },
        "plannings": {
            "heating_prog_a": len(data.week_planning),
            "heating_prog_b": len(data.week_planning2),
            "cooling_prog_c": len(data.week_planning3),
            "cooling_prog_d": len(data.week_planning4),
        },
        "api": api.get_diagnostic_info(),
    }

    return diagnostics
