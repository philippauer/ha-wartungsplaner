"""Binary sensor platform for the Wartungsplaner integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WartungsplanerCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor entities from a config entry."""
    coordinator: WartungsplanerCoordinator = hass.data[DOMAIN]["coordinator"]

    known_task_ids: set[str] = set()

    @callback
    def _async_add_new_sensors() -> None:
        """Add binary sensors for newly discovered tasks."""
        if coordinator.data is None:
            return

        tasks = coordinator.data.get("tasks", {})
        new_entities = []

        for task_id in tasks:
            if task_id not in known_task_ids:
                known_task_ids.add(task_id)
                new_entities.append(
                    WartungsplanerTaskBinarySensor(coordinator, task_id)
                )

        # Remove entities for deleted tasks
        current_ids = set(tasks.keys())
        removed_ids = known_task_ids - current_ids
        if removed_ids:
            ent_reg = er.async_get(hass)
            for task_id in removed_ids:
                entity_id = ent_reg.async_get_entity_id(
                    "binary_sensor", DOMAIN, f"wartungsplaner_task_due_{task_id}"
                )
                if entity_id:
                    ent_reg.async_remove(entity_id)
        known_task_ids.intersection_update(current_ids)

        if new_entities:
            async_add_entities(new_entities)

    _async_add_new_sensors()

    entry.async_on_unload(
        coordinator.async_add_listener(_async_add_new_sensors)
    )


class WartungsplanerTaskBinarySensor(
    CoordinatorEntity[WartungsplanerCoordinator], BinarySensorEntity
):
    """Binary sensor entity for a maintenance task (due/overdue = ON)."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self,
        coordinator: WartungsplanerCoordinator,
        task_id: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._task_id = task_id
        self._attr_unique_id = f"wartungsplaner_task_due_{task_id}"

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
        """Return the name of the binary sensor."""
        task = self._task_data
        if task:
            return f"{task['name']} fällig"
        return f"Task {self._task_id[:8]} fällig"

    @property
    def is_on(self) -> bool | None:
        """Return True if the task is due or overdue."""
        task = self._task_data
        if task is None:
            return None

        status = task.get("status")
        return status in ("due", "overdue", "never_done")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        task = self._task_data
        if task is None:
            return {}

        return {
            "task_id": self._task_id,
            "status": task.get("status"),
            "next_due": task.get("next_due"),
            "days_until_due": task.get("days_until_due"),
            "task_name": task.get("name"),
        }
