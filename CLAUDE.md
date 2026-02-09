# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Wartungsplaner is a HACS Custom Integration for Home Assistant that manages household maintenance tasks. It provides a sidebar panel (vanilla Web Component), sensors/binary sensors per task, a calendar, 5 services, and a WebSocket API. Fully bilingual (German/English), no external dependencies beyond HA built-ins.

## Architecture

```
Store (JSON persistence via .storage/wartungsplaner.tasks)
  → Coordinator (status computation, 1h interval)
    → Entities (sensor, binary_sensor, calendar)
  → WebSocket API (16 commands) ← Frontend Panel (Shadow DOM Web Component)
  → Services (5 HA services)
```

**Setup sequence** (`__init__.py`): Load store → create coordinator → first refresh → register WS API → register services → register panel → forward to entity platforms.

**Shared state** via `hass.data[DOMAIN]`: Keys are `"store"`, `"coordinator"`, `"entry"`. Both WS handlers and services access store/coordinator through this dict.

**Data flow**: Frontend calls WS commands → WS handler mutates store → calls `coordinator.async_request_refresh()` → coordinator recomputes statuses/stats → entities update via `CoordinatorEntity`. The coordinator's `_async_update_data` also fires `EVENT_TASK_DUE`/`EVENT_TASK_OVERDUE` on status transitions (comparing against `_previous_statuses`).

**Entity lifecycle**: Sensor and binary sensor platforms use `coordinator.async_add_listener()` with a closure that tracks `known_task_ids`. New tasks spawn new entities; deleted tasks are removed from the entity registry via `er.async_get()` + `async_remove()`. The calendar is a single entity covering all tasks.

**Panel registration**: Uses `async_register_built_in_panel` with `component_name="custom"`. Static files served from `frontend/` directory via `StaticPathConfig`.

## Key Files

| File | Role |
|------|------|
| `__init__.py` | Entry point, services, panel registration |
| `store.py` | Persistent storage (tasks, custom templates, custom categories, hidden templates, settings) |
| `coordinator.py` | `DataUpdateCoordinator` — computes status, fires transition events, reads `due_soon_days` from store |
| `websocket_api.py` | 16 WS commands (task CRUD, templates, categories, settings) |
| `frontend/wartungsplaner-panel.js` | Entire UI — vanilla Web Component with Shadow DOM, no build step |
| `templates.py` | 44 predefined German household task templates |
| `const.py` | Enums (`TaskCategory`, `TaskPriority`, `IntervalUnit`, `TaskStatus`), labels, icons |
| `config_flow.py` | Single-instance config flow (only `enable_notifications`; `due_soon_days` is in panel settings) |

## Conventions

- **Storage**: `helpers.storage.Store` with key `wartungsplaner.tasks`, version 1. Top-level keys: `tasks`, `custom_templates`, `custom_categories`, `hidden_templates`, `settings`. New keys are additive (no version bump needed).
- **Time calculations**: `dateutil.relativedelta` (bundled with HA) for months/years intervals.
- **Category validation**: Relaxed to `str` (not `vol.In`) to support custom categories.
- **Slugify**: Use `from slugify import slugify` (python-slugify), NOT `homeassistant.util.slugify`.
- **Entity unique IDs**: `wartungsplaner_task_{uuid}` (sensor), `wartungsplaner_task_due_{uuid}` (binary sensor), `wartungsplaner_calendar` (calendar).
- **WS command format**: `wartungsplaner/{command}`, decorated with `@websocket_api.websocket_command`. Sync handlers use `@callback`, async handlers use `@websocket_api.async_response`.
- **WS handler pattern**: After any store mutation, always call `await coordinator.async_request_refresh()` before sending the result.
- **Frontend i18n**: `STRINGS` object with `de`/`en` keys, language detected from `hass.language`.
- **Frontend dialogs**: Created as DOM elements appended to shadowRoot, removed on close.
- **Labels**: All enums have bilingual `{de, en}` label dicts in `const.py` (`CATEGORY_LABELS`, `PRIORITY_LABELS`, `STATUS_LABELS`).

## Development Notes

- No build step, test suite, or linter configured. The frontend JS is served directly.
- Python syntax check: `python3 -c "import ast; ast.parse(open('file.py').read())"`
- JS syntax check: `node -e "new (require('vm').Script)(require('fs').readFileSync('file.js','utf8'))"`
- Version lives in `manifest.json` (`"version": "x.y.z"`).
- Releases are created via `gh release create vX.Y.Z` with German changelog.
- The integration is single-instance only (`async_set_unique_id(DOMAIN)` in config flow).
