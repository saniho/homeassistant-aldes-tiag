"""Support for the Aldes binary sensors."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, FRIENDLY_NAMES, MANUFACTURER
from .entity import AldesEntity, DeviceContext

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from custom_components.aldes.coordinator import AldesDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add Aldes binary sensors from a config_entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    binary_sensors: list[AldesBinarySensorEntity | AldesFilterSensorEntity] = []

    for device_key, device in (coordinator.data or {}).items():
        if not device:
            continue
        context = DeviceContext(
            device_key=device_key,
            device=device,
            config_entry=entry,
        )
        binary_sensors.extend(
            [
                AldesBinarySensorEntity(coordinator, context),
                AldesFilterSensorEntity(coordinator, context),
            ]
        )

    async_add_entities(binary_sensors)


class AldesBinarySensorEntity(AldesEntity, BinarySensorEntity):
    """Define an Aldes binary sensor."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self,
        coordinator: AldesDataUpdateCoordinator,
        context: DeviceContext,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, context)

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
        return f"{self.serial_number}_connectivity"

    def _friendly_name_internal(self) -> str | None:
        """Return the friendly name."""
        return "Connectivité"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update attributes when the coordinator updates."""
        self._async_update_attrs()
        super()._handle_coordinator_update()

    @callback
    def _async_update_attrs(self) -> None:
        """Update binary sensor attributes."""
        device = self._get_device()
        self._attr_is_on = bool(
            self.serial_number and device is not None and device.is_connected
        )


class AldesFilterSensorEntity(AldesEntity, BinarySensorEntity):
    """Define an Aldes filter wear binary sensor."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self,
        coordinator: AldesDataUpdateCoordinator,
        context: DeviceContext,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, context)

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
        return f"{self.serial_number}_filter_wear"

    def _friendly_name_internal(self) -> str | None:
        """Return the friendly name."""
        return "Usure du filtre"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update attributes when the coordinator updates."""
        self._async_update_attrs()
        super()._handle_coordinator_update()

    @callback
    def _async_update_attrs(self) -> None:
        """Update filter sensor attributes."""
        device = self._get_device()
        if device is not None:
            # Convert None to False (0), otherwise use the boolean value
            filter_wear = device.filter_wear
            self._attr_is_on = bool(filter_wear) if filter_wear is not None else False
            # Add last update date as extra state attribute
            self._attr_extra_state_attributes = {
                "date_dernier_changement": device.date_last_filter_update
            }
        else:
            self._attr_is_on = False
