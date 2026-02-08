"""AldesEntity class."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.aldes.coordinator import AldesDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class AldesEntity(CoordinatorEntity):
    """Aldes entity."""

    coordinator: AldesDataUpdateCoordinator
    serial_number: str
    reference: str
    modem: str
    is_connected: bool

    def __init__(
        self,
        coordinator: AldesDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the AldesEntity."""
        super().__init__(coordinator)
        self._attr_config_entry = config_entry
        self.serial_number = coordinator.data.serial_number
        self.reference = coordinator.data.reference
        self.modem = coordinator.data.modem
        self.is_connected = coordinator.data.is_connected

    @property
    def name(self) -> str | None:
        """Return the name of the entity."""
        return self._friendly_name_internal()

    def _friendly_name_internal(self) -> str | None:
        """Return the friendly name - to be overridden by subclasses."""
        return None
