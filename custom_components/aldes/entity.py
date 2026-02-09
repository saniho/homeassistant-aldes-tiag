"""AldesEntity class."""

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.aldes.const import AirMode, HouseholdComposition, WaterMode
from custom_components.aldes.coordinator import AldesDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class SettingsApiEntity:
    """Settings Api Entity."""

    people: HouseholdComposition | None
    antilegio: int | None
    kwh_creuse: float | None
    kwh_pleine: float | None

    def __init__(self, data: dict[str, Any] | None) -> None:
        """Initialize."""
        self.people = data.get("people") if data else None
        self.antilegio = data.get("antilegio") if data else None
        self.kwh_creuse = data.get("kwh_creuse") if data else None
        self.kwh_pleine = data.get("kwh_pleine") if data else None


class IndicatorApiEntity:
    """Thermistat Api Entity."""

    # Heat temperatur min
    fmist: int
    # Heat temperatur max
    fmast: int
    # Cool temperatur min
    cmast: int
    # Cool temperatur max
    cmist: int
    # Hot water quantity in %
    hot_water_quantity: int
    # Main temperature in °C
    main_temperature: float
    # Current air mode, default A = OFF
    current_air_mode: AirMode = AirMode.OFF
    # Current water mode, default L = OFF
    current_water_mode: WaterMode = WaterMode.OFF

    settings: SettingsApiEntity

    def __init__(self, data: dict[str, Any] | None) -> None:
        """Initialize."""
        self.fmist = data.get("fmist", 0) if data else 0
        self.fmast = data.get("fmast", 0) if data else 0
        self.cmast = data.get("cmast", 0) if data else 0
        self.cmist = data.get("cmist", 0) if data else 0
        self.hot_water_quantity = data.get("qte_eau_chaude", 0) if data else 0
        self.main_temperature = data.get("tmp_principal", 0) if data else 0
        self.current_air_mode = data.get("current_air_mode") if data else AirMode.OFF
        self.current_water_mode = (
            data.get("current_water_mode") if data else WaterMode.OFF
        )
        self.settings = SettingsApiEntity(data.get("settings") if data else None)

        if data and data.get("thermostats"):
            # Thermostats
            self.thermostats: list[ThermostatApiEntity] = [
                ThermostatApiEntity(t) for t in data["thermostats"]
            ]
        else:
            self.thermostats = []


class ThermostatApiEntity:
    """Thermistat Api Entity."""

    id: int
    name: str
    number: int
    temperature_set: int
    current_temperature: float

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize."""
        self.id = data["ThermostatId"]
        self.name = data["Name"]
        self.number = data["Number"]
        self.temperature_set = data["TemperatureSet"]
        self.current_temperature = data["CurrentTemperature"]


class DataApiEntity:
    """Data API Entity."""

    indicator: IndicatorApiEntity
    last_updated_date: str
    modem: str
    reference: str
    serial_number: str
    type: str
    filter_wear: bool
    date_last_filter_update: str
    has_filter: bool
    is_connected: bool
    week_planning: list[dict[str, str]]
    week_planning2: list[dict[str, str]]
    week_planning3: list[dict[str, str]]
    week_planning4: list[dict[str, str]]
    holidays_start: str | None
    holidays_end: str | None
    hors_gel: bool

    def __init__(self, data: dict[str, Any] | None) -> None:
        """Initialize."""
        self.indicator = IndicatorApiEntity(data["indicator"] if data else None)
        self.last_updated_date = data["lastUpdatedDate"] if data else ""
        self.modem = data["modem"] if data else ""
        self.reference = data["reference"] if data else ""
        self.serial_number = data["serial_number"] if data else ""
        self.type = data["type"] if data else ""
        self.filter_wear = data["usureFiltre"] if data else False
        self.date_last_filter_update = data["dateLastFilterUpdate"] if data else ""
        self.has_filter = data["hasFilter"] if data else False
        self.is_connected = data["isConnected"] if data else False
        self.week_planning = data["week_planning"] if data else []
        self.week_planning2 = data["week_planning2"] if data else []
        self.week_planning3 = data["week_planning3"] if data else []
        self.week_planning4 = data["week_planning4"] if data else []

        # Parse holidays dates and frost protection from indicator if available
        self.holidays_start = None
        self.holidays_end = None
        self.hors_gel = False
        if data and "indicator" in data and data["indicator"]:
            indicator_data = data["indicator"]
            self.holidays_start = indicator_data.get("date_debut_vac")
            self.holidays_end = indicator_data.get("date_fin_vac")
            self.hors_gel = indicator_data.get("hors_gel", False)

        _LOGGER.debug(
            "DataApiEntity initialized - Device: %s (%s), Connected: %s, "
            "Plannings loaded: week_planning=%d, week_planning2=%d, "
            "week_planning3=%d, week_planning4=%d",
            self.reference,
            self.type,
            self.is_connected,
            len(self.week_planning),
            len(self.week_planning2),
            len(self.week_planning3),
            len(self.week_planning4),
        )


@dataclass(frozen=True)
class DeviceContext:
    """Context for a specific Aldes device."""

    device_key: str
    device: DataApiEntity
    config_entry: ConfigEntry


class AldesEntity(CoordinatorEntity):
    """Aldes entity."""

    coordinator: AldesDataUpdateCoordinator
    _device_key: str
    serial_number: str
    reference: str
    modem: str
    is_connected: bool

    def __init__(
        self,
        coordinator: AldesDataUpdateCoordinator,
        context: DeviceContext,
    ) -> None:
        """Initialize the AldesEntity."""
        super().__init__(coordinator)
        self._attr_config_entry = context.config_entry
        self._device_key = context.device_key
        self.serial_number = context.device.serial_number
        self.reference = context.device.reference
        self.modem = context.device.modem
        self.is_connected = context.device.is_connected

    def _get_device(self) -> DataApiEntity | None:
        """Return current device data from the coordinator."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self._device_key)

    @property
    def name(self) -> str | None:
        """Return the name of the entity."""
        return self._friendly_name_internal()

    def _friendly_name_internal(self) -> str | None:
        """Return the friendly name - to be overridden by subclasses."""
        return None
