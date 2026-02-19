"""AldesEntity class."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.aldes.const import (
    VERIFY_STATE_CHANGE_DELAY,
    VERIFY_STATE_CHANGE_REFRESH_DELAY,
)
from custom_components.aldes.coordinator import AldesDataUpdateCoordinator
from custom_components.aldes.models import DataApiEntity

_LOGGER = logging.getLogger(__name__)


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

    @property
    def device_identifier(self) -> str:
        """
        Return a stable identifier for the device.

        Preference order: `serial_number` (if present and not 'N/A'), then `modem`,
        then internal `_device_key` as a last resort.
        """
        # Preference: serial (to preserve existing entity IDs) -> modem -> device_key
        try:
            serial = (self.serial_number or "").strip()
        except (AttributeError, TypeError):
            serial = ""
        if serial and serial.upper() != "N/A":
            return serial

        try:
            modem = (self.modem or "").strip()
        except (AttributeError, TypeError):
            modem = ""
        if modem:
            return modem

        return str(self._device_key)

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

    async def _verify_state_change_after_delay(  # noqa: PLR0913
        self,
        get_current_fn: Callable[[], Any],
        expected_value: Any,
        retry_fn: Callable[[], Awaitable[None]],
        threshold: float = 0,
        command_name: str = "change",
        max_retries: int = 1,
    ) -> None:
        """
        Verify a state change was applied after a delay and retry if needed.

        Generic method for verifying that any state change (temperature, mode, etc.)
        was actually applied by the API, and retry if not.

        Args:
            get_current_fn: Callable that returns the current value from device data
            expected_value: The value we expect to have after the command
            retry_fn: Async callable to retry the command if not applied
            threshold: Maximum allowed difference for numeric values (default 0)
            command_name: Name of the command for logging (default "change")
            max_retries: Maximum number of retry attempts (default 1)

        """
        try:
            for attempt in range(1, max_retries + 1):
                await asyncio.sleep(VERIFY_STATE_CHANGE_DELAY)

                # Force a coordinator refresh to get latest data
                await self.coordinator.async_request_refresh()
                await asyncio.sleep(VERIFY_STATE_CHANGE_REFRESH_DELAY)

                # Get current value
                current_value = get_current_fn()

                # Check if the state was actually updated
                is_changed = (
                    abs(current_value - expected_value) <= threshold
                    if isinstance(expected_value, int | float)
                    else current_value == expected_value
                )

                if is_changed:
                    _LOGGER.debug(
                        "%s successfully updated to %s (attempt %d/%d)",
                        command_name.title(),
                        expected_value,
                        attempt,
                        max_retries,
                    )
                    break

                # Not changed - log attempt and retry if we have attempts remaining
                if attempt < max_retries:
                    _LOGGER.warning(
                        "%s not updated after %d seconds (attempt %d/%d, "
                        "expected: %s, actual: %s). Retrying...",
                        command_name.title(),
                        VERIFY_STATE_CHANGE_DELAY,
                        attempt,
                        max_retries,
                        expected_value,
                        current_value,
                    )
                    # Retry the command
                    await retry_fn()
                else:
                    _LOGGER.warning(
                        "%s not updated after %d seconds (final attempt %d/%d, "
                        "expected: %s, actual: %s)",
                        command_name.title(),
                        VERIFY_STATE_CHANGE_DELAY,
                        attempt,
                        max_retries,
                        expected_value,
                        current_value,
                    )

        except asyncio.CancelledError:
            _LOGGER.debug("%s verification cancelled", command_name.title())
        except Exception:
            _LOGGER.exception("Error verifying %s", command_name)
