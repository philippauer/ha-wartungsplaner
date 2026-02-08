"""DataUpdateCoordinator for the Wartungsplaner integration."""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_DUE_SOON_DAYS,
    DEFAULT_DUE_SOON_DAYS,
    DOMAIN,
    EVENT_TASK_DUE,
    EVENT_TASK_OVERDUE,
    UPDATE_INTERVAL,
    TaskStatus,
)
from .store import WartungsplanerStore

_LOGGER = logging.getLogger(__name__)


class WartungsplanerCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage task data and status computation."""

    def __init__(
        self,
        hass: HomeAssistant,
        store: WartungsplanerStore,
        due_soon_days: int = DEFAULT_DUE_SOON_DAYS,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.store = store
        self.due_soon_days = due_soon_days
        self._previous_statuses: dict[str, str] = {}

    def _compute_task_status(self, task: dict[str, Any]) -> str:
        """Compute the current status of a task."""
        today = date.today()
        next_due_str = task.get("next_due")

        if next_due_str is None:
            return TaskStatus.NEVER_DONE

        next_due = date.fromisoformat(next_due_str)

        if next_due < today:
            return TaskStatus.OVERDUE
        if next_due == today:
            return TaskStatus.DUE
        if next_due <= today + timedelta(days=self.due_soon_days):
            return TaskStatus.DUE_SOON

        return TaskStatus.DONE

    def _compute_days_until_due(self, task: dict[str, Any]) -> int | None:
        """Compute days until a task is due."""
        next_due_str = task.get("next_due")
        if next_due_str is None:
            return None
        next_due = date.fromisoformat(next_due_str)
        return (next_due - date.today()).days

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch and compute task data."""
        tasks = self.store.tasks
        task_data: dict[str, Any] = {}
        stats = {
            "total": 0,
            "overdue": 0,
            "due_soon": 0,
            "due": 0,
            "done": 0,
            "never_done": 0,
        }

        for task_id, task in tasks.items():
            status = self._compute_task_status(task)
            days_until_due = self._compute_days_until_due(task)

            task_data[task_id] = {
                **task,
                "status": status,
                "days_until_due": days_until_due,
            }

            stats["total"] += 1
            if status == TaskStatus.OVERDUE:
                stats["overdue"] += 1
            elif status == TaskStatus.DUE_SOON:
                stats["due_soon"] += 1
            elif status == TaskStatus.DUE:
                stats["due"] += 1
            elif status == TaskStatus.DONE:
                stats["done"] += 1
            elif status == TaskStatus.NEVER_DONE:
                stats["never_done"] += 1

            # Fire events on status transitions
            prev_status = self._previous_statuses.get(task_id)
            if prev_status is not None and prev_status != status:
                if status == TaskStatus.DUE:
                    self.hass.bus.async_fire(
                        EVENT_TASK_DUE,
                        {
                            "task_id": task_id,
                            "task_name": task["name"],
                            "category": task["category"],
                            "priority": task["priority"],
                            "next_due": task["next_due"],
                        },
                    )
                elif status == TaskStatus.OVERDUE:
                    self.hass.bus.async_fire(
                        EVENT_TASK_OVERDUE,
                        {
                            "task_id": task_id,
                            "task_name": task["name"],
                            "category": task["category"],
                            "priority": task["priority"],
                            "next_due": task["next_due"],
                        },
                    )

            self._previous_statuses[task_id] = status

        # Clean up removed tasks from previous statuses
        current_ids = set(tasks.keys())
        for old_id in list(self._previous_statuses.keys()):
            if old_id not in current_ids:
                del self._previous_statuses[old_id]

        return {"tasks": task_data, "stats": stats}
