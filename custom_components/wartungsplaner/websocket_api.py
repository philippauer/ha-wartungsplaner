"""WebSocket API for the Wartungsplaner integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import (
    CATEGORY_ICONS,
    CATEGORY_LABELS,
    DOMAIN,
    IntervalUnit,
    TaskCategory,
    TaskPriority,
)
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
    websocket_api.async_register_command(hass, ws_get_categories)
    websocket_api.async_register_command(hass, ws_add_category)
    websocket_api.async_register_command(hass, ws_delete_category)
    websocket_api.async_register_command(hass, ws_add_custom_template)
    websocket_api.async_register_command(hass, ws_delete_custom_template)
    websocket_api.async_register_command(hass, ws_restore_hidden_templates)
    websocket_api.async_register_command(hass, ws_get_settings)
    websocket_api.async_register_command(hass, ws_update_settings)
    websocket_api.async_register_command(hass, ws_suggest_description)


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
        vol.Optional("category", default="other"): str,
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
        vol.Optional("category"): str,
        vol.Optional("priority"): vol.In([e.value for e in TaskPriority]),
        vol.Optional("interval_value"): vol.All(
            vol.Coerce(int), vol.Range(min=1)
        ),
        vol.Optional("interval_unit"): vol.In(
            [e.value for e in IntervalUnit]
        ),
        vol.Optional("last_completed"): str,
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
    store = _get_store(hass)
    builtin = [t for t in get_templates() if t["id"] not in store.hidden_templates]
    custom = list(store.custom_templates.values())
    hidden_count = len(store.hidden_templates)
    connection.send_result(msg["id"], {
        "templates": builtin + custom,
        "hidden_count": hidden_count,
    })


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
        # Check custom templates
        template = store.custom_templates.get(msg["template_id"])
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


# --- Categories ---


@websocket_api.websocket_command(
    {
        vol.Required("type"): "wartungsplaner/get_categories",
    }
)
@callback
def ws_get_categories(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle get categories WebSocket command."""
    store = _get_store(hass)
    # Built-in categories
    builtin = []
    for cat in TaskCategory:
        builtin.append({
            "id": cat.value,
            "name_de": CATEGORY_LABELS[cat]["de"],
            "name_en": CATEGORY_LABELS[cat]["en"],
            "icon": CATEGORY_ICONS[cat],
            "builtin": True,
        })
    # Custom categories
    custom = [
        {**c, "builtin": False} for c in store.custom_categories.values()
    ]
    connection.send_result(msg["id"], {"categories": builtin + custom})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "wartungsplaner/add_category",
        vol.Required("name_de"): str,
        vol.Required("name_en"): str,
        vol.Optional("icon", default="mdi:dots-horizontal"): str,
    }
)
@websocket_api.async_response
async def ws_add_category(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle add category WebSocket command."""
    store = _get_store(hass)
    category = await store.async_add_category({
        "name_de": msg["name_de"],
        "name_en": msg["name_en"],
        "icon": msg.get("icon", "mdi:dots-horizontal"),
    })
    connection.send_result(msg["id"], {"category": category})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "wartungsplaner/delete_category",
        vol.Required("category_id"): str,
    }
)
@websocket_api.async_response
async def ws_delete_category(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle delete category WebSocket command."""
    store = _get_store(hass)
    success = await store.async_delete_category(msg["category_id"])
    if not success:
        connection.send_error(
            msg["id"], "cannot_delete", "Category not found or in use by tasks"
        )
        return
    connection.send_result(msg["id"], {"success": True})


# --- Custom Templates ---


@websocket_api.websocket_command(
    {
        vol.Required("type"): "wartungsplaner/add_custom_template",
        vol.Required("name"): str,
        vol.Optional("description", default=""): str,
        vol.Optional("category", default="other"): str,
        vol.Optional("priority", default="medium"): vol.In(
            [e.value for e in TaskPriority]
        ),
        vol.Optional("interval_value", default=1): vol.All(
            vol.Coerce(int), vol.Range(min=1)
        ),
        vol.Optional("interval_unit", default="months"): vol.In(
            [e.value for e in IntervalUnit]
        ),
    }
)
@websocket_api.async_response
async def ws_add_custom_template(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle add custom template WebSocket command."""
    store = _get_store(hass)
    template = await store.async_add_custom_template({
        "name": msg["name"],
        "description": msg.get("description", ""),
        "category": msg.get("category", "other"),
        "priority": msg.get("priority", "medium"),
        "interval_value": msg.get("interval_value", 1),
        "interval_unit": msg.get("interval_unit", "months"),
    })
    connection.send_result(msg["id"], {"template": template})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "wartungsplaner/delete_custom_template",
        vol.Required("template_id"): str,
    }
)
@websocket_api.async_response
async def ws_delete_custom_template(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle delete template WebSocket command (custom or builtin)."""
    store = _get_store(hass)
    template_id = msg["template_id"]

    # Try custom template first
    if template_id in store.custom_templates:
        await store.async_delete_custom_template(template_id)
        connection.send_result(msg["id"], {"success": True})
        return

    # Try hiding a builtin template
    if get_template_by_id(template_id):
        await store.async_hide_builtin_template(template_id)
        connection.send_result(msg["id"], {"success": True})
        return

    connection.send_error(msg["id"], "not_found", "Template not found")


@websocket_api.websocket_command(
    {
        vol.Required("type"): "wartungsplaner/restore_hidden_templates",
    }
)
@websocket_api.async_response
async def ws_restore_hidden_templates(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle restore hidden builtin templates WebSocket command."""
    store = _get_store(hass)
    await store.async_restore_hidden_templates()
    connection.send_result(msg["id"], {"success": True})


# --- Settings ---


@websocket_api.websocket_command(
    {
        vol.Required("type"): "wartungsplaner/get_settings",
    }
)
@callback
def ws_get_settings(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle get settings WebSocket command."""
    store = _get_store(hass)
    connection.send_result(msg["id"], {"settings": store.settings})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "wartungsplaner/update_settings",
        vol.Optional("due_soon_days"): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=90)
        ),
        vol.Optional("conversation_agent_id"): str,
    }
)
@websocket_api.async_response
async def ws_update_settings(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle update settings WebSocket command."""
    store = _get_store(hass)
    coordinator = _get_coordinator(hass)

    data = {k: v for k, v in msg.items() if k not in ("id", "type")}
    settings = await store.async_update_settings(data)
    await coordinator.async_request_refresh()
    connection.send_result(msg["id"], {"settings": settings})


# --- AI Description Suggestion ---


@websocket_api.websocket_command(
    {
        vol.Required("type"): "wartungsplaner/suggest_description",
        vol.Required("task_name"): str,
        vol.Optional("category"): str,
        vol.Optional("language", default="de"): vol.In(["de", "en"]),
    }
)
@websocket_api.async_response
async def ws_suggest_description(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle suggest description WebSocket command using conversation agent."""
    task_name = msg["task_name"]
    language = msg.get("language", "de")
    category_id = msg.get("category")

    # Resolve category label for the prompt
    category_label = ""
    if category_id:
        try:
            cat_enum = TaskCategory(category_id)
            category_label = CATEGORY_LABELS[cat_enum][language]
        except (ValueError, KeyError):
            # Custom category — use the raw id as label
            category_label = category_id

    if language == "de":
        prompt = (
            f"Erstelle eine kurze, praktische Beschreibung (2-3 Sätze) für die "
            f"Hauswartungsaufgabe '{task_name}'"
        )
        if category_label:
            prompt += f" in der Kategorie '{category_label}'"
        prompt += ". Beschreibe konkret was zu tun ist. Antworte nur mit der Beschreibung."
    else:
        prompt = (
            f"Create a short, practical description (2-3 sentences) for the "
            f"household maintenance task '{task_name}'"
        )
        if category_label:
            prompt += f" in the category '{category_label}'"
        prompt += ". Describe specifically what needs to be done. Reply only with the description."

    # Use configured agent or fall back to default
    store = _get_store(hass)
    agent_id = store.settings.get("conversation_agent_id")

    service_data = {"text": prompt, "language": language}
    if agent_id:
        service_data["agent_id"] = agent_id

    try:
        result = await hass.services.async_call(
            "conversation",
            "process",
            service_data,
            blocking=True,
            return_response=True,
        )
        _LOGGER.debug("Conversation result: %s", result)

        response_data = result.get("response", {})

        # Check if the conversation agent returned an error intent
        response_type = response_data.get("response_type")
        intent_code = response_data.get("data", {}).get("code")
        if response_type == "error" or intent_code == "no_intent_match":
            _LOGGER.warning(
                "Conversation agent returned error: type=%s, code=%s",
                response_type,
                intent_code,
            )
            connection.send_error(
                msg["id"],
                "no_ai_agent",
                "No AI conversation agent configured",
            )
            return

        speech = response_data.get("speech", {}).get("plain", {}).get("speech", "")

        if not speech or len(speech) < 20:
            connection.send_error(
                msg["id"],
                "no_ai_agent",
                "No AI conversation agent configured",
            )
            return

        connection.send_result(msg["id"], {"description": speech})
    except Exception:
        _LOGGER.exception("Failed to get AI description suggestion")
        connection.send_error(
            msg["id"], "conversation_failed", "Failed to generate description"
        )
