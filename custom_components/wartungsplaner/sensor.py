"""Sensor platform for the Wartungsplaner integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CATEGORY_LABELS, DOMAIN, PRIORITY_LABELS, STATUS_LABELS
from .coordinator import WartungsplanerCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities from a config entry."""
    coordinator: WartungsplanerCoordinator = hass.data[DOMAIN]["coordinator"]

    known_task_ids: set[str] = set()

    @callback
    def _async_add_new_sensors() -> None:
        """Add sensors for newly discovered tasks."""
        if coordinator.data is None:
            return

        tasks = coordinator.data.get("tasks", {})
        new_entities = []

        for task_id in tasks:
            if task_id not in known_task_ids:
                known_task_ids.add(task_id)
                new_entities.append(
                    WartungsplanerTaskSensor(coordinator, task_id)
                )

        # Remove tracked IDs for deleted tasks
        current_ids = set(tasks.keys())
        known_task_ids.intersection_update(current_ids)

        if new_entities:
            async_add_entities(new_entities)

    # Add existing tasks
    _async_add_new_sensors()

    # Listen for future updates to add new tasks dynamically
    entry.async_on_unload(
        coordinator.async_add_listener(_async_add_new_sensors)
    )


class WartungsplanerTaskSensor(
    CoordinatorEntity[WartungsplanerCoordinator], SensorEntity
):
    """Sensor entity for a maintenance task (days until due)."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = "days"
    _attr_icon = "mdi:wrench-clock"

    def __init__(
        self,
        coordinator: WartungsplanerCoordinator,
        task_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._task_id = task_id
        self._attr_unique_id = f"wartungsplaner_task_{task_id}"

    @property
    def _task_data(self) -> dict[str, Any] | None:
        """Get the current task data from coordinator."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("tasks", {}).get(self._task_id)

    @property
    def available(self) -> bool:
        """Return True if the task still exists."""
        return self._task_data is not None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        task = self._task_data
        if task:
            return task["name"]
        return f"Task {self._task_id[:8]}"

    @property
    def native_value(self) -> int | None:
        """Return the number of days until the task is due."""
        task = self._task_data
        if task is None:
            return None
        return task.get("days_until_due")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        task = self._task_data
        if task is None:
            return {}

        status = task.get("status", "unknown")
        category = task.get("category", "other")
        priority = task.get("priority", "medium")

        return {
            "task_id": self._task_id,
            "status": status,
            "status_label": STATUS_LABELS.get(status, {}).get("de", status),
            "category": category,
            "category_label": CATEGORY_LABELS.get(category, {}).get("de", category),
            "priority": priority,
            "priority_label": PRIORITY_LABELS.get(priority, {}).get("de", priority),
            "next_due": task.get("next_due"),
            "last_completed": task.get("last_completed"),
            "interval_value": task.get("interval_value"),
            "interval_unit": task.get("interval_unit"),
            "description": task.get("description", ""),
            "snoozed_until": task.get("snoozed_until"),
        }

    @property
    def icon(self) -> str:
        """Return the icon based on task status."""
        task = self._task_data
        if task is None:
            return "mdi:wrench-clock"

        status = task.get("status")
        if status == "overdue":
            return "mdi:alert-circle"
        if status == "due":
            return "mdi:alert"
        if status == "due_soon":
            return "mdi:clock-alert"
        if status == "never_done":
            return "mdi:help-circle"
        return "mdi:check-circle"
