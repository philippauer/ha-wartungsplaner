# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Wartungsplaner is a HACS Custom Integration for Home Assistant that manages household maintenance tasks. It provides a sidebar panel (vanilla Web Component), sensors/binary sensors per task, a calendar, 5 services, and a WebSocket API. Fully bilingual (German/English), no external dependencies beyond HA built-ins.

## Architecture

```
Store (JSON persistence)
  → Coordinator (status computation, 1h interval)
    → Entities (sensor, binary_sensor, calendar)
  → WebSocket API (14 commands) ← Frontend Panel (Shadow DOM Web Component)
  → Services (5 HA services)
```

**Setup sequence** (`__init__.py`): Load store → create coordinator → first refresh → register WS API → register services → register panel → forward to entity platforms.

**Entity lifecycle**: Entities are created dynamically via `coordinator.async_add_listener()`. When tasks are deleted, entities are removed from the entity registry via `er.async_get()` + `async_remove()`.

**Panel registration**: Uses `async_register_built_in_panel` with `component_name="custom"`. Static files served from `frontend/` directory.

## Key Files

| File | Role |
|------|------|
| `__init__.py` | Entry point, services, panel registration |
| `store.py` | Persistent storage (tasks, custom templates, custom categories, hidden templates) |
| `coordinator.py` | `DataUpdateCoordinator` — computes status, fires transition events |
| `websocket_api.py` | 14 WS commands (task CRUD, templates, categories) |
| `frontend/wartungsplaner-panel.js` | Entire UI — vanilla Web Component with Shadow DOM, no build step |
| `templates.py` | 44 predefined German household task templates |
| `const.py` | Enums (`TaskCategory`, `TaskPriority`, `IntervalUnit`, `TaskStatus`), labels, icons |
| `config_flow.py` | Single-instance config with options flow |

## Conventions

- **Storage**: `helpers.storage.Store` with key `wartungsplaner.tasks`, version 1. New top-level keys are additive (no version bump needed).
- **Time calculations**: `dateutil.relativedelta` (bundled with HA) for months/years intervals.
- **Category validation**: Relaxed to `str` (not `vol.In`) to support custom categories.
- **Slugify**: Use `from slugify import slugify` (python-slugify), NOT `homeassistant.util.slugify`.
- **Entity unique IDs**: `wartungsplaner_task_{uuid}` (sensor), `wartungsplaner_task_due_{uuid}` (binary sensor).
- **WS command format**: `wartungsplaner/{command}`, decorated with `@websocket_api.websocket_command`.
- **Frontend i18n**: `STRINGS` object with `de`/`en` keys, language detected from `hass.language`.
- **Frontend dialogs**: Created as DOM elements appended to shadowRoot, removed on close.

## Development Notes

- No build step, test suite, or linter configured. The frontend JS is served directly.
- Python syntax check: `python3 -c "import ast; ast.parse(open('file.py').read())"`
- JS syntax check: `node -e "new (require('vm').Script)(require('fs').readFileSync('file.js','utf8'))"`
- Version lives in `manifest.json` (`"version": "x.y.z"`).
- Releases are created via `gh release create vX.Y.Z` with German changelog.
- The integration is single-instance only (`async_set_unique_id(DOMAIN)` in config flow).
