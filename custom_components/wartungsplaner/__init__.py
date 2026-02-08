"""The Wartungsplaner integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.components.frontend import async_register_built_in_panel
from homeassistant.components.http import StaticPathConfig

from .const import (
    DOMAIN,
    PLATFORMS,
)
from .coordinator import WartungsplanerCoordinator
from .store import WartungsplanerStore
from .websocket_api import async_register_websocket_api

_LOGGER = logging.getLogger(__name__)

SERVICE_COMPLETE_TASK = "complete_task"
SERVICE_ADD_TASK = "add_task"
SERVICE_UPDATE_TASK = "update_task"
SERVICE_DELETE_TASK = "delete_task"
SERVICE_SNOOZE_TASK = "snooze_task"

SERVICE_COMPLETE_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
        vol.Optional("notes", default=""): cv.string,
    }
)

SERVICE_ADD_SCHEMA = vol.Schema(
    {
        vol.Required("name"): cv.string,
        vol.Optional("description", default=""): cv.string,
        vol.Optional("category", default="other"): cv.string,
        vol.Optional("priority", default="medium"): cv.string,
        vol.Optional("interval_value", default=1): vol.All(
            vol.Coerce(int), vol.Range(min=1)
        ),
        vol.Optional("interval_unit", default="months"): cv.string,
    }
)

SERVICE_UPDATE_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
        vol.Optional("name"): cv.string,
        vol.Optional("description"): cv.string,
        vol.Optional("category"): cv.string,
        vol.Optional("priority"): cv.string,
        vol.Optional("interval_value"): vol.All(
            vol.Coerce(int), vol.Range(min=1)
        ),
        vol.Optional("interval_unit"): cv.string,
    }
)

SERVICE_DELETE_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
    }
)

SERVICE_SNOOZE_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
        vol.Required("until_date"): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Wartungsplaner from a config entry."""
    store = WartungsplanerStore(hass)
    await store.async_load()

    coordinator = WartungsplanerCoordinator(hass, store)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["store"] = store
    hass.data[DOMAIN]["coordinator"] = coordinator
    hass.data[DOMAIN]["entry"] = entry

    # Register WebSocket API
    async_register_websocket_api(hass)

    # Register services
    await _async_register_services(hass, store, coordinator)

    # Register frontend panel
    await _async_register_panel(hass)

    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data.pop(DOMAIN, None)

    return unload_ok


async def _async_register_panel(hass: HomeAssistant) -> None:
    """Register the frontend panel."""
    panel_url = "/wartungsplaner_panel"
    panel_path = hass.config.path(
        "custom_components/wartungsplaner/frontend"
    )

    await hass.http.async_register_static_paths(
        [StaticPathConfig(panel_url, panel_path, cache_headers=False)]
    )

    async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title="Wartungsplaner",
        sidebar_icon="mdi:wrench-clock",
        frontend_url_path="wartungsplaner",
        config={
            "_panel_custom": {
                "name": "wartungsplaner-panel",
                "module_url": f"{panel_url}/wartungsplaner-panel.js",
            }
        },
        require_admin=False,
    )


async def _async_register_services(
    hass: HomeAssistant,
    store: WartungsplanerStore,
    coordinator: WartungsplanerCoordinator,
) -> None:
    """Register integration services."""

    async def handle_complete_task(call: ServiceCall) -> None:
        """Handle the complete_task service call."""
        task_id = call.data["task_id"]
        notes = call.data.get("notes", "")
        result = await store.async_complete_task(task_id, notes)
        if result:
            await coordinator.async_request_refresh()

    async def handle_add_task(call: ServiceCall) -> None:
        """Handle the add_task service call."""
        task_data: dict[str, Any] = dict(call.data)
        await store.async_add_task(task_data)
        await coordinator.async_request_refresh()

    async def handle_update_task(call: ServiceCall) -> None:
        """Handle the update_task service call."""
        task_id = call.data["task_id"]
        task_data = {
            k: v for k, v in call.data.items() if k != "task_id"
        }
        result = await store.async_update_task(task_id, task_data)
        if result:
            await coordinator.async_request_refresh()

    async def handle_delete_task(call: ServiceCall) -> None:
        """Handle the delete_task service call."""
        task_id = call.data["task_id"]
        result = await store.async_delete_task(task_id)
        if result:
            await coordinator.async_request_refresh()

    async def handle_snooze_task(call: ServiceCall) -> None:
        """Handle the snooze_task service call."""
        task_id = call.data["task_id"]
        until_date = call.data["until_date"]
        result = await store.async_snooze_task(task_id, until_date)
        if result:
            await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN, SERVICE_COMPLETE_TASK, handle_complete_task, SERVICE_COMPLETE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_ADD_TASK, handle_add_task, SERVICE_ADD_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_TASK, handle_update_task, SERVICE_UPDATE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_DELETE_TASK, handle_delete_task, SERVICE_DELETE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SNOOZE_TASK, handle_snooze_task, SERVICE_SNOOZE_SCHEMA
    )
