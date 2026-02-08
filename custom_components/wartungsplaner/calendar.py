"""Calendar platform for the Wartungsplaner integration."""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Any

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CATEGORY_LABELS, DOMAIN, PRIORITY_LABELS
from .coordinator import WartungsplanerCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the calendar entity from a config entry."""
    coordinator: WartungsplanerCoordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities([WartungsplanerCalendar(coordinator)])


class WartungsplanerCalendar(
    CoordinatorEntity[WartungsplanerCoordinator], CalendarEntity
):
    """Calendar entity showing maintenance task due dates."""

    _attr_has_entity_name = True
    _attr_name = "Wartungsplaner"
    _attr_unique_id = "wartungsplaner_calendar"
    _attr_icon = "mdi:calendar-wrench"

    def __init__(self, coordinator: WartungsplanerCoordinator) -> None:
        """Initialize the calendar entity."""
        super().__init__(coordinator)

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming calendar event."""
        events = self._get_all_events()
        if not events:
            return None

        today = date.today()
        # Find the closest event to today (could be past for overdue)
        upcoming = [e for e in events if e.start >= today]
        if upcoming:
            upcoming.sort(key=lambda e: e.start)
            return upcoming[0]

        # All events are in the past (overdue), return the most recent
        events.sort(key=lambda e: e.start, reverse=True)
        return events[0]

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a date range."""
        events = self._get_all_events()
        start = start_date.date() if isinstance(start_date, datetime) else start_date
        end = end_date.date() if isinstance(end_date, datetime) else end_date

        return [
            e
            for e in events
            if e.start < end and e.end > start
        ]

    def _get_all_events(self) -> list[CalendarEvent]:
        """Get all calendar events from tasks."""
        if self.coordinator.data is None:
            return []

        tasks = self.coordinator.data.get("tasks", {})
        events: list[CalendarEvent] = []

        for task_id, task in tasks.items():
            next_due_str = task.get("next_due")
            if next_due_str is None:
                continue

            try:
                due_date = date.fromisoformat(next_due_str)
            except (ValueError, TypeError):
                continue

            category = task.get("category", "other")
            priority = task.get("priority", "medium")
            cat_label = CATEGORY_LABELS.get(category, {}).get("de", category)
            prio_label = PRIORITY_LABELS.get(priority, {}).get("de", priority)

            description = task.get("description", "")
            summary_parts = [f"[{cat_label}]", task["name"]]
            desc_parts = [
                f"Priorität: {prio_label}",
                f"Kategorie: {cat_label}",
            ]
            if description:
                desc_parts.append(f"\n{description}")

            event = CalendarEvent(
                start=due_date,
                end=due_date + timedelta(days=1),
                summary=" ".join(summary_parts),
                description="\n".join(desc_parts),
                uid=f"wartungsplaner_{task_id}",
            )
            events.append(event)

        return events
