"""WebSocket API for the Wartungsplaner integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN, IntervalUnit, TaskCategory, TaskPriority
from .templates import get_template_by_id, get_templates

_LOGGER = logging.getLogger(__name__)


def async_register_websocket_api(hass: HomeAssistant) -> None:
    """Register WebSocket API handlers."""
    websocket_api.async_register_command(hass, ws_get_tasks)
    websocket_api.async_register_command(hass, ws_add_task)
    websocket_api.async_register_command(hass, ws_update_task)
    websocket_api.async_register_command(hass, ws_delete_task)
    websocket_api.async_register_command(hass, ws_complete_task)
    websocket_api.async_register_command(hass, ws_get_templates)
    websocket_api.async_register_command(hass, ws_add_from_template)
    websocket_api.async_register_command(hass, ws_snooze_task)


def _get_coordinator(hass: HomeAssistant):
    """Get the coordinator from hass data."""
    return hass.data[DOMAIN]["coordinator"]


def _get_store(hass: HomeAssistant):
    """Get the store from hass data."""
    return hass.data[DOMAIN]["store"]


@websocket_api.websocket_command(
    {
        vol.Required("type"): "wartungsplaner/get_tasks",
    }
)
@callback
def ws_get_tasks(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle get tasks WebSocket command."""
    coordinator = _get_coordinator(hass)
    data = coordinator.data or {"tasks": {}, "stats": {}}
    connection.send_result(msg["id"], data)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "wartungsplaner/add_task",
        vol.Required("name"): str,
        vol.Optional("description", default=""): str,
        vol.Optional("category", default="other"): vol.In(
            [e.value for e in TaskCategory]
        ),
        vol.Optional("priority", default="medium"): vol.In(
            [e.value for e in TaskPriority]
        ),
        vol.Optional("interval_value", default=1): vol.All(
            vol.Coerce(int), vol.Range(min=1)
        ),
        vol.Optional("interval_unit", default="months"): vol.In(
            [e.value for e in IntervalUnit]
        ),
        vol.Optional("last_completed"): str,
    }
)
@websocket_api.async_response
async def ws_add_task(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle add task WebSocket command."""
    store = _get_store(hass)
    coordinator = _get_coordinator(hass)

    task_data = {
        "name": msg["name"],
        "description": msg.get("description", ""),
        "category": msg.get("category", "other"),
        "priority": msg.get("priority", "medium"),
        "interval_value": msg.get("interval_value", 1),
        "interval_unit": msg.get("interval_unit", "months"),
        "last_completed": msg.get("last_completed"),
    }

    task = await store.async_add_task(task_data)
    await coordinator.async_request_refresh()
    connection.send_result(msg["id"], {"task": task})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "wartungsplaner/update_task",
        vol.Required("task_id"): str,
        vol.Optional("name"): str,
        vol.Optional("description"): str,
        vol.Optional("category"): vol.In([e.value for e in TaskCategory]),
        vol.Optional("priority"): vol.In([e.value for e in TaskPriority]),
        vol.Optional("interval_value"): vol.All(
            vol.Coerce(int), vol.Range(min=1)
        ),
        vol.Optional("interval_unit"): vol.In(
            [e.value for e in IntervalUnit]
        ),
    }
)
@websocket_api.async_response
async def ws_update_task(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle update task WebSocket command."""
    store = _get_store(hass)
    coordinator = _get_coordinator(hass)

    task_id = msg["task_id"]
    task_data = {
        k: v
        for k, v in msg.items()
        if k not in ("id", "type", "task_id") and v is not None
    }

    task = await store.async_update_task(task_id, task_data)
    if task is None:
        connection.send_error(msg["id"], "not_found", "Task not found")
        return

    await coordinator.async_request_refresh()
    connection.send_result(msg["id"], {"task": task})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "wartungsplaner/delete_task",
        vol.Required("task_id"): str,
    }
)
@websocket_api.async_response
async def ws_delete_task(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle delete task WebSocket command."""
    store = _get_store(hass)
    coordinator = _get_coordinator(hass)

    success = await store.async_delete_task(msg["task_id"])
    if not success:
        connection.send_error(msg["id"], "not_found", "Task not found")
        return

    await coordinator.async_request_refresh()
    connection.send_result(msg["id"], {"success": True})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "wartungsplaner/complete_task",
        vol.Required("task_id"): str,
        vol.Optional("notes", default=""): str,
    }
)
@websocket_api.async_response
async def ws_complete_task(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle complete task WebSocket command."""
    store = _get_store(hass)
    coordinator = _get_coordinator(hass)

    task = await store.async_complete_task(msg["task_id"], msg.get("notes"))
    if task is None:
        connection.send_error(msg["id"], "not_found", "Task not found")
        return

    await coordinator.async_request_refresh()
    connection.send_result(msg["id"], {"task": task})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "wartungsplaner/get_templates",
    }
)
@callback
def ws_get_templates(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle get templates WebSocket command."""
    templates = get_templates()
    connection.send_result(msg["id"], {"templates": templates})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "wartungsplaner/add_from_template",
        vol.Required("template_id"): str,
    }
)
@websocket_api.async_response
async def ws_add_from_template(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle add task from template WebSocket command."""
    store = _get_store(hass)
    coordinator = _get_coordinator(hass)

    template = get_template_by_id(msg["template_id"])
    if template is None:
        connection.send_error(msg["id"], "not_found", "Template not found")
        return

    task_data = {
        "name": template["name"],
        "description": template["description"],
        "category": template["category"],
        "priority": template["priority"],
        "interval_value": template["interval_value"],
        "interval_unit": template["interval_unit"],
    }

    task = await store.async_add_task(task_data)
    await coordinator.async_request_refresh()
    connection.send_result(msg["id"], {"task": task})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "wartungsplaner/snooze_task",
        vol.Required("task_id"): str,
        vol.Required("until_date"): str,
    }
)
@websocket_api.async_response
async def ws_snooze_task(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle snooze task WebSocket command."""
    store = _get_store(hass)
    coordinator = _get_coordinator(hass)

    task = await store.async_snooze_task(msg["task_id"], msg["until_date"])
    if task is None:
        connection.send_error(msg["id"], "not_found", "Task not found")
        return

    await coordinator.async_request_refresh()
    connection.send_result(msg["id"], {"task": task})
