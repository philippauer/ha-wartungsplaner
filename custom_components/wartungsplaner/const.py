"""Constants for the Wartungsplaner integration."""

from enum import StrEnum

DOMAIN = "wartungsplaner"

# Storage
STORAGE_KEY = "wartungsplaner.tasks"
STORAGE_VERSION = 1

# Config keys
CONF_DUE_SOON_DAYS = "due_soon_days"
CONF_ENABLE_NOTIFICATIONS = "enable_notifications"

# Defaults
DEFAULT_DUE_SOON_DAYS = 7
DEFAULT_ENABLE_NOTIFICATIONS = True

# Update interval (seconds)
UPDATE_INTERVAL = 3600  # 1 hour

# Events
EVENT_TASK_DUE = "wartungsplaner_task_due"
EVENT_TASK_OVERDUE = "wartungsplaner_task_overdue"

# Platforms
PLATFORMS = ["sensor", "binary_sensor", "calendar"]


class TaskCategory(StrEnum):
    """Task categories."""

    HEATING = "heating"
    SAFETY = "safety"
    PLUMBING = "plumbing"
    APPLIANCES = "appliances"
    EXTERIOR = "exterior"
    INTERIOR = "interior"
    ELECTRICAL = "electrical"
    GARDEN = "garden"
    CLEANING = "cleaning"
    OTHER = "other"


CATEGORY_LABELS = {
    TaskCategory.HEATING: {"de": "Heizung", "en": "Heating"},
    TaskCategory.SAFETY: {"de": "Sicherheit", "en": "Safety"},
    TaskCategory.PLUMBING: {"de": "Sanitär", "en": "Plumbing"},
    TaskCategory.APPLIANCES: {"de": "Geräte", "en": "Appliances"},
    TaskCategory.EXTERIOR: {"de": "Außen", "en": "Exterior"},
    TaskCategory.INTERIOR: {"de": "Innen", "en": "Interior"},
    TaskCategory.ELECTRICAL: {"de": "Elektrik", "en": "Electrical"},
    TaskCategory.GARDEN: {"de": "Garten", "en": "Garden"},
    TaskCategory.CLEANING: {"de": "Reinigung", "en": "Cleaning"},
    TaskCategory.OTHER: {"de": "Sonstiges", "en": "Other"},
}


class TaskPriority(StrEnum):
    """Task priorities."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


PRIORITY_LABELS = {
    TaskPriority.LOW: {"de": "Niedrig", "en": "Low"},
    TaskPriority.MEDIUM: {"de": "Mittel", "en": "Medium"},
    TaskPriority.HIGH: {"de": "Hoch", "en": "High"},
    TaskPriority.CRITICAL: {"de": "Kritisch", "en": "Critical"},
}


class IntervalUnit(StrEnum):
    """Interval units for task scheduling."""

    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"


class TaskStatus(StrEnum):
    """Computed task status."""

    DONE = "done"
    DUE_SOON = "due_soon"
    DUE = "due"
    OVERDUE = "overdue"
    NEVER_DONE = "never_done"


STATUS_LABELS = {
    TaskStatus.DONE: {"de": "Erledigt", "en": "Done"},
    TaskStatus.DUE_SOON: {"de": "Bald fällig", "en": "Due soon"},
    TaskStatus.DUE: {"de": "Fällig", "en": "Due"},
    TaskStatus.OVERDUE: {"de": "Überfällig", "en": "Overdue"},
    TaskStatus.NEVER_DONE: {"de": "Nie erledigt", "en": "Never done"},
}
