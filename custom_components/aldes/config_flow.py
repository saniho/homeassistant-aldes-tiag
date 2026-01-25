"""Adds config flow for Aldes."""

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import AldesApi, AuthenticationError
from .const import (
    CONF_PASSWORD,
    CONF_PERFORMANCE_LOGS,
    CONF_USERNAME,
    DOMAIN,
)


class AldesFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Aldes."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self) -> None:
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> Any:
        """Handle a flow initialized by the user."""
        self._errors = {}

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            valid = await self._test_credentials(
                user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
            )
            if valid:
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME], data=user_input
                )
            self._errors["base"] = "auth"
            return await self._show_config_form(user_input)

        user_input = {}
        # Provide defaults for form
        user_input[CONF_USERNAME] = ""
        user_input[CONF_PASSWORD] = ""

        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return AldesOptionsFlowHandler(config_entry)

    async def _show_config_form(self, user_input: dict[str, str]) -> Any:
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME, default=user_input[CONF_USERNAME]): str,  # type: ignore  # noqa: PGH003
                    vol.Required(CONF_PASSWORD, default=user_input[CONF_PASSWORD]): str,  # type: ignore  # noqa: PGH003
                }
            ),
            errors=self._errors,
        )

    async def _test_credentials(self, username: str, password: str) -> bool:
        """Return true if credentials is valid."""
        try:
            session = async_create_clientsession(self.hass)
            api = AldesApi(username, password, session)
            await api.authenticate()
        except AuthenticationError:
            return False
        else:
            return True

    async def async_migrate_entry(
        self, hass: HomeAssistant, entry: config_entries.ConfigEntry
    ) -> bool:
        """Migrate old entry."""
        if "token" not in entry.options:
            hass.config_entries.async_update_entry(
                entry,
                options={**entry.options, "token": ""},
            )
        return True


class AldesOptionsFlowHandler(config_entries.OptionsFlow):
    """Aldes config flow options handler."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        # Explicitly call the parent's __init__ method
        config_entries.OptionsFlow.__init__(self, config_entry)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_PERFORMANCE_LOGS,
                        default=self.config_entry.options.get(
                            CONF_PERFORMANCE_LOGS, False
                        ),
                    ): bool,
                }
            ),
        )
