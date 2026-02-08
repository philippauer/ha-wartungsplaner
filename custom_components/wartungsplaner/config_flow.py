"""Config flow for the Wartungsplaner integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_ENABLE_NOTIFICATIONS,
    DEFAULT_ENABLE_NOTIFICATIONS,
    DOMAIN,
)


class WartungsplanerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Wartungsplaner."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        # Only allow a single instance
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(
                title="Wartungsplaner",
                data={},
                options={
                    CONF_ENABLE_NOTIFICATIONS: user_input.get(
                        CONF_ENABLE_NOTIFICATIONS, DEFAULT_ENABLE_NOTIFICATIONS
                    ),
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ENABLE_NOTIFICATIONS,
                        default=DEFAULT_ENABLE_NOTIFICATIONS,
                    ): bool,
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow handler."""
        return WartungsplanerOptionsFlow(config_entry)


class WartungsplanerOptionsFlow(OptionsFlow):
    """Handle options flow for Wartungsplaner."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ENABLE_NOTIFICATIONS,
                        default=self.config_entry.options.get(
                            CONF_ENABLE_NOTIFICATIONS, DEFAULT_ENABLE_NOTIFICATIONS
                        ),
                    ): bool,
                }
            ),
        )
