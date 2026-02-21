# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Workflow

**Always use a git worktree when working on an issue.** Create a worktree per issue branch rather than working directly on `master`:

```bash
git worktree add ../ha-arctic-spa-issue-42 -b fix/issue-42
cd ../ha-arctic-spa-issue-42
```

**Commit messages must reference the issue number** using the format `type(#N): description`, e.g.:
- `fix(#2): add None guard in sensor.py native_value`
- `feat(#8): add reauth flow for expired API keys`
- `docs(#12): add Known Limitations section to README`

**Branch protection:** `master` is protected. All changes go through PRs. Do not commit directly to `master`.

## Commands

```bash
# Install dev dependencies
uv sync

# Run tests
uv run pytest tests/ -v

# Run a single test
uv run pytest tests/test_api.py::test_get_status -v

# Lint
uv run ruff check custom_components/arctic_spa

# Format check
uv run ruff format --check custom_components/arctic_spa

# Auto-fix lint issues
uv run ruff check --fix custom_components/arctic_spa

# Pre-commit (prek — drop-in replacement for pre-commit, Rust-based, uses .pre-commit-config.yaml)
prek run --all-files
```

## Architecture

This is a Home Assistant custom integration. Data flows in one direction:

```
Arctic Spa Cloud API (myarcticspa.com/v2/spa)
  ↓ ArcticSpaClient (api.py)         — aiohttp HTTP client, raises on errors
  ↓ ArcticSpaCoordinator (coordinator.py) — polls every 60s, wraps errors as UpdateFailed/ConfigEntryAuthFailed
  ↓ entry.runtime_data               — coordinator stored on the config entry
  ├→ sensor.py                       — read-only sensors (temp, pH, ORP, pump states, errors)
  ├→ binary_sensor.py                — read-only binary sensors (connectivity, running states)
  ├→ switch.py                       — command entities (lights, pumps, boost)
  └→ number.py                       — slider controls (setpoint, filtration)
```

**Key patterns:**

- **`api.py`** is HA-free. `ArcticSpaClient` takes an optional `aiohttp.ClientSession`. All methods raise `ArcticSpaAuthError`, `ArcticSpaApiError`, or `ArcticSpaConnectionError` on failure — they never return `False` or swallow errors.
- **`coordinator.py`** converts `ArcticSpaAuthError` → `ConfigEntryAuthFailed` (triggers HA reauth flow) and `ArcticSpaApiError` → `UpdateFailed`.
- **`entity.py`** defines `ArcticSpaEntity(CoordinatorEntity)` — the base for all entities. It sets `_attr_has_entity_name = True` and provides `device_info`. Unique IDs follow `{entry_id}_{key}`.
- **Platform files** (`sensor.py`, `binary_sensor.py`, `switch.py`, `number.py`) read the coordinator via `entry.runtime_data`. Command handlers (`async_turn_on`, `async_set_native_value`, etc.) call the client and request a coordinator refresh; they catch `ArcticSpaApiError` and log errors rather than raising.
- **`config_flow.py`** validates the API key by making a live call. It also implements `async_step_reauth_confirm` for re-authentication. Uses `async_get_clientsession(self.hass)` for the validation call.
- **`SpaStatus` dataclass** in `api.py` exists but the coordinator uses `async_get_status_raw()` (returns `dict`) rather than the typed version. Entities read coordinator data as `dict` using `.get()` with defaults.
- **Boost Mode** is the only stateful switch — the API does not expose boost state, so it is tracked locally in `self._is_on` and resets on HA restart.

## HA-specific conventions

- Use `UnitOfTemperature.FAHRENHEIT` and `UnitOfTime.HOURS` — not raw strings — for HA unit conversion support.
- Set `_attr_entity_category = EntityCategory.DIAGNOSTIC` on connectivity/error/status sensors and `EntityCategory.CONFIG` on filtration controls and boost.
- The integration targets HA 2024.1.0+ (`manifest.json` `homeassistant` minimum).

## Release process

Releases are triggered by publishing a GitHub Release with a `v*` tag. The `release.yml` workflow updates `manifest.json` version and uploads `arctic_spa.zip`. Release notes are auto-drafted by Release Drafter from PR titles.

## Testing

Tests live in `tests/test_api.py` and mock `aiohttp` directly via `sys.modules`. Run with `pytest-asyncio` in `auto` mode. There are currently no tests for coordinator, config flow, or platform entities — new tests for those should use `pytest-homeassistant-custom-component`.
