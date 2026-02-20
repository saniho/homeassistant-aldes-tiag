"""
Integration test: load platforms and verify unique_ids for multi-device case.

These are lightweight integration-style tests that avoid pytest asyncio
fixtures and instead use a small dummy ``hass``-like object.
"""

import sys
from pathlib import Path
from types import SimpleNamespace

# Make repo root importable
ROOT = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, ROOT)

from custom_components.aldes.const import DOMAIN  # noqa: E402
from custom_components.aldes.entity import DataApiEntity  # noqa: E402

SAMPLE_DEVICES = [
    {
        "indicator": {
            "fmist": 22,
            "fmast": 31,
            "cmast": 24,
            "cmist": 16,
            "qte_eau_chaude": 0,
            "tmp_principal": 21.37,
            "current_air_mode": "B",
            "current_water_mode": "L",
            "thermostats": [],
            "settings": {
                "people": 2,
                "antilegio": 0,
                "kwh_creuse": 0.12,
                "kwh_pleine": 0.219,
            },
        },
        "modem": "289C6E2E9D9A",
        "reference": "TONE_AIR",
        "serial_number": "N/A",
        "isConnected": True,
        "usureFiltre": None,
        "dateLastFilterUpdate": None,
        "hasFilter": None,
        "week_planning": [],
        "week_planning2": [],
        "week_planning3": [],
        "week_planning4": [],
    },
    {
        "indicator": {
            "fmist": 22,
            "fmast": 31,
            "cmast": 24,
            "cmist": 16,
            "qte_eau_chaude": 50,
            "tmp_principal": 21.18,
            "current_air_mode": "B",
            "current_water_mode": "M",
            "thermostats": [],
            "settings": {
                "people": 2,
                "antilegio": 0,
                "kwh_creuse": 0.12,
                "kwh_pleine": 0.253,
            },
        },
        "modem": "289C6E2EA378",
        "reference": "TONE_AQUA_AIR",
        "serial_number": "N/A",
        "isConnected": True,
        "usureFiltre": None,
        "dateLastFilterUpdate": None,
        "hasFilter": None,
        "week_planning": [],
        "week_planning2": [],
        "week_planning3": [],
        "week_planning4": [],
    },
]


def _normalize(payload: dict) -> dict:
    """Normalize payload with required default fields."""
    p = dict(payload)
    p.setdefault("usureFiltre", None)
    p.setdefault("dateLastFilterUpdate", None)
    p.setdefault("hasFilter", None)
    p.setdefault("isConnected", True)
    p.setdefault("week_planning", [])
    p.setdefault("week_planning2", [])
    p.setdefault("week_planning3", [])
    p.setdefault("week_planning4", [])
    p.setdefault("lastUpdatedDate", "")
    p.setdefault("type", "")
    return p


def test_platforms_create_unique_ids() -> None:
    """Load platforms and assert unique_ids are modem-based and unique."""
    import asyncio

    loop = asyncio.new_event_loop()

    class DummyHass:
        """Minimal hass-like object for platform setup calls."""

        def __init__(self) -> None:
            """Initialize dummy hass."""
            self.data: dict = {}
            self.loop = loop

    hass = DummyHass()

    devices: dict[str, DataApiEntity] = {}
    for d in SAMPLE_DEVICES:
        devices[d["modem"]] = DataApiEntity(_normalize(d))

    class DummyCoordinator:
        """Minimal coordinator-like object with data."""

        def __init__(self, data: dict) -> None:
            """Initialize coordinator with data."""
            self.data = data

    coordinator = DummyCoordinator(devices)

    entry_id = "test_entry"
    hass.data.setdefault(DOMAIN, {})[entry_id] = coordinator

    entry = SimpleNamespace(entry_id=entry_id, data={}, options={})

    created: list[object] = []

    def async_add_entities(ents: list[object]) -> None:
        """Capture created entities."""
        created.extend(ents)

    from custom_components.aldes import (
        binary_sensor,
        button,
        number,
        select,
        sensor,
        text,
    )

    hass.loop.run_until_complete(
        binary_sensor.async_setup_entry(hass, entry, async_add_entities)
    )
    hass.loop.run_until_complete(
        sensor.async_setup_entry(hass, entry, async_add_entities)
    )
    hass.loop.run_until_complete(
        select.async_setup_entry(hass, entry, async_add_entities)
    )
    hass.loop.run_until_complete(
        text.async_setup_entry(hass, entry, async_add_entities)
    )
    hass.loop.run_until_complete(
        button.async_setup_entry(hass, entry, async_add_entities)
    )
    hass.loop.run_until_complete(
        number.async_setup_entry(hass, entry, async_add_entities)
    )

    assert created, "No entities created by platforms"  # noqa: S101

    unique_ids = [
        getattr(e, "unique_id", None) or getattr(e, "_attr_unique_id", None)
        for e in created
    ]
    unique_ids = [u for u in unique_ids if u]

    assert len(unique_ids) == len(set(unique_ids))  # noqa: S101

    modems = set(devices.keys())
    assert all(any(u.startswith(m + "_") for m in modems) for u in unique_ids)  # noqa: S101

    for m in modems:
        assert f"{m}_connectivity" in unique_ids  # noqa: S101
