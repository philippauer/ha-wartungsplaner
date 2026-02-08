"""Persistent storage for the Wartungsplaner integration."""

from __future__ import annotations

import logging
import uuid
from datetime import date, datetime
from typing import Any

from dateutil.relativedelta import relativedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN, STORAGE_KEY, STORAGE_VERSION, IntervalUnit

_LOGGER = logging.getLogger(__name__)


def _calculate_next_due(
    last_completed: str | None,
    interval_value: int,
    interval_unit: str,
    snoozed_until: str | None = None,
) -> str | None:
    """Calculate the next due date based on last completion and interval."""
    if last_completed is None:
        return None

    base_date = date.fromisoformat(last_completed)

    if interval_unit == IntervalUnit.DAYS:
        next_due = base_date + relativedelta(days=interval_value)
    elif interval_unit == IntervalUnit.WEEKS:
        next_due = base_date + relativedelta(weeks=interval_value)
    elif interval_unit == IntervalUnit.MONTHS:
        next_due = base_date + relativedelta(months=interval_value)
    elif interval_unit == IntervalUnit.YEARS:
        next_due = base_date + relativedelta(years=interval_value)
    else:
        return None

    # If snoozed, use snooze date if it's later
    if snoozed_until:
        snooze_date = date.fromisoformat(snoozed_until)
        if snooze_date > next_due:
            next_due = snooze_date

    return next_due.isoformat()


class WartungsplanerStore:
    """Handle persistent storage for tasks."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the store."""
        self._hass = hass
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._tasks: dict[str, dict[str, Any]] = {}

    @property
    def tasks(self) -> dict[str, dict[str, Any]]:
        """Return all tasks."""
        return self._tasks

    async def async_load(self) -> None:
        """Load data from storage."""
        data = await self._store.async_load()
        if data and "tasks" in data:
            self._tasks = data["tasks"]
        else:
            self._tasks = {}
        _LOGGER.debug("Loaded %d tasks from storage", len(self._tasks))

    async def async_save(self) -> None:
        """Save data to storage."""
        await self._store.async_save({"tasks": self._tasks})

    async def async_add_task(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Add a new task."""
        task_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        task = {
            "id": task_id,
            "name": task_data["name"],
            "description": task_data.get("description", ""),
            "category": task_data.get("category", "other"),
            "priority": task_data.get("priority", "medium"),
            "interval_value": task_data.get("interval_value", 1),
            "interval_unit": task_data.get("interval_unit", "months"),
            "last_completed": task_data.get("last_completed"),
            "completion_history": [],
            "next_due": None,
            "snoozed_until": None,
            "created_at": now,
            "updated_at": now,
        }

        # Calculate next_due
        task["next_due"] = _calculate_next_due(
            task["last_completed"],
            task["interval_value"],
            task["interval_unit"],
        )

        self._tasks[task_id] = task
        await self.async_save()
        _LOGGER.debug("Added task: %s (%s)", task["name"], task_id)
        return task

    async def async_update_task(
        self, task_id: str, task_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update an existing task."""
        if task_id not in self._tasks:
            _LOGGER.warning("Task not found: %s", task_id)
            return None

        task = self._tasks[task_id]

        for key in (
            "name",
            "description",
            "category",
            "priority",
            "interval_value",
            "interval_unit",
        ):
            if key in task_data:
                task[key] = task_data[key]

        task["updated_at"] = datetime.now().isoformat()

        # Recalculate next_due
        task["next_due"] = _calculate_next_due(
            task["last_completed"],
            task["interval_value"],
            task["interval_unit"],
            task.get("snoozed_until"),
        )

        await self.async_save()
        _LOGGER.debug("Updated task: %s (%s)", task["name"], task_id)
        return task

    async def async_delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        if task_id not in self._tasks:
            _LOGGER.warning("Task not found for deletion: %s", task_id)
            return False

        name = self._tasks[task_id]["name"]
        del self._tasks[task_id]
        await self.async_save()
        _LOGGER.debug("Deleted task: %s (%s)", name, task_id)
        return True

    async def async_complete_task(
        self, task_id: str, notes: str | None = None
    ) -> dict[str, Any] | None:
        """Mark a task as completed."""
        if task_id not in self._tasks:
            _LOGGER.warning("Task not found for completion: %s", task_id)
            return None

        task = self._tasks[task_id]
        today = date.today().isoformat()

        completion_entry = {
            "date": today,
            "notes": notes or "",
            "timestamp": datetime.now().isoformat(),
        }
        task["completion_history"].append(completion_entry)
        task["last_completed"] = today
        task["snoozed_until"] = None

        # Recalculate next_due
        task["next_due"] = _calculate_next_due(
            task["last_completed"],
            task["interval_value"],
            task["interval_unit"],
        )
        task["updated_at"] = datetime.now().isoformat()

        await self.async_save()
        _LOGGER.debug("Completed task: %s (%s)", task["name"], task_id)
        return task

    async def async_snooze_task(
        self, task_id: str, until_date: str
    ) -> dict[str, Any] | None:
        """Snooze a task until a specific date."""
        if task_id not in self._tasks:
            _LOGGER.warning("Task not found for snooze: %s", task_id)
            return None

        task = self._tasks[task_id]
        task["snoozed_until"] = until_date

        # Recalculate next_due with snooze
        task["next_due"] = _calculate_next_due(
            task["last_completed"],
            task["interval_value"],
            task["interval_unit"],
            until_date,
        )
        task["updated_at"] = datetime.now().isoformat()

        await self.async_save()
        _LOGGER.debug("Snoozed task: %s until %s", task["name"], until_date)
        return task
