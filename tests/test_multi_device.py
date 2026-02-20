"""Unit tests for multi-device handling and unique_id construction."""

import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

# Ensure local `custom_components` package is importable in tests
ROOT = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, ROOT)

from homeassistant.core import HomeAssistant  # noqa: E402

from custom_components.aldes.entity import (  # noqa: E402
    AldesEntity,
    DataApiEntity,
    DeviceContext,
)

SAMPLE_AQUAAIR = {
    "indicator": {
        "fmist": 22,
        "fmast": 31,
        "cmast": 24,
        "cmist": 16,
        "qte_eau_chaude": 75,
        "tmp_principal": 19.81,
        "current_air_mode": "B",
        "current_water_mode": "M",
        "thermostats": [
            {
                "ThermostatId": 1,
                "Name": "T1",
                "Number": 0,
                "TemperatureSet": 20,
                "CurrentTemperature": 19.8,
            }
        ],
        "settings": {
            "people": 2,
            "antilegio": 0,
            "kwh_creuse": 0.138,
            "kwh_pleine": 0.173,
        },
    },
    "lastUpdatedDate": "2026-02-10 14:14:54Z",
    "modem": "MODem_A",
    "reference": "TONE_AQUA_AIR",
    "serial_number": "SN_A",
    "type": "TONE",
    "isConnected": True,
    "week_planning": [{"command": "00C"}],
}


SAMPLE_TONE = {
    "indicator": {
        "fmist": 20,
        "fmast": 30,
        "cmast": 22,
        "cmist": 15,
        "qte_eau_chaude": 50,
        "tmp_principal": 18.0,
        "current_air_mode": "A",
        "current_water_mode": "L",
        "thermostats": [
            {
                "ThermostatId": 2,
                "Name": "T2",
                "Number": 0,
                "TemperatureSet": 19,
                "CurrentTemperature": 18.0,
            }
        ],
        "settings": {
            "people": 1,
            "antilegio": 0,
            "kwh_creuse": 0.15,
            "kwh_pleine": 0.2,
        },
    },
    "lastUpdatedDate": "2026-02-10 14:15:00Z",
    "modem": "MODEM_B",
    "reference": "TONE",
    "serial_number": "SN_B",
    "type": "TONE",
    "isConnected": False,
    "week_planning": [{"command": "00C"}],
}


@pytest.fixture
async def prepare_hass(
    hass: HomeAssistant, aiohttp_client: Any
) -> tuple[HomeAssistant, object]:
    """
    Prepare a hass instance and a coordinator populated with two devices.

    Returns a tuple of (hass, coordinator-like-object).
    """
    from custom_components.aldes.api import AldesApi
    from custom_components.aldes.coordinator import AldesDataUpdateCoordinator

    api = AldesApi("u", "p", aiohttp_client)
    coord = AldesDataUpdateCoordinator(hass, api)

    devices = {
        SAMPLE_AQUAAIR["modem"]: DataApiEntity(SAMPLE_AQUAAIR),
        SAMPLE_TONE["modem"]: DataApiEntity(SAMPLE_TONE),
    }

    hass.data.setdefault("aldes", {})["test_entry"] = coord
    coord.data = devices
    return hass, coord


def test_entities_unique_ids_for_multi_device() -> None:
    """Verify device_identifier and unique_id construction for two devices."""

    def normalize(payload: dict) -> dict:
        """Ensure sample payloads contain expected keys used by DataApiEntity."""
        p = dict(payload)
        p.setdefault("usureFiltre", False)
        p.setdefault("dateLastFilterUpdate", "")
        p.setdefault("hasFilter", False)
        p.setdefault("isConnected", False)
        p.setdefault("week_planning", [])
        p.setdefault("week_planning2", [])
        p.setdefault("week_planning3", [])
        p.setdefault("week_planning4", [])
        p.setdefault("lastUpdatedDate", "")
        return p

    a = DataApiEntity(normalize(SAMPLE_AQUAAIR))
    b = DataApiEntity(normalize(SAMPLE_TONE))

    class DummyCoordinator:
        """Minimal dummy coordinator with data attribute."""

        def __init__(self, data: dict) -> None:
            """Initialize coordinator with data."""
            self.data = data

    devices = {SAMPLE_AQUAAIR["modem"]: a, SAMPLE_TONE["modem"]: b}
    coord = DummyCoordinator(devices)

    entry = SimpleNamespace(entry_id="test_entry")

    a_context = DeviceContext(
        device_key=SAMPLE_AQUAAIR["modem"], device=a, config_entry=entry
    )
    b_context = DeviceContext(
        device_key=SAMPLE_TONE["modem"], device=b, config_entry=entry
    )

    a_ent = AldesEntity(coord, a_context)
    b_ent = AldesEntity(coord, b_context)

    assert a_ent.device_identifier == SAMPLE_AQUAAIR["serial_number"]  # noqa: S101
    assert b_ent.device_identifier == SAMPLE_TONE["serial_number"]  # noqa: S101

    expected_ids_count = 4

    ids = {
        f"{a_ent.device_identifier}_connectivity",
        f"{a_ent.device_identifier}_filter_wear",
        f"{b_ent.device_identifier}_connectivity",
        f"{b_ent.device_identifier}_filter_wear",
    }
    assert len(ids) == expected_ids_count  # noqa: S101
