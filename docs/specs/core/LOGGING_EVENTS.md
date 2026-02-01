Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# LOGGING_EVENTS

This document defines the structured event log schema used by launcher and setup. Events are emitted via `core_log` as deterministic TLV records (no free-form strings in kernel code).

## Model
- `core_log_event`: `domain`, `code`, `severity`, `flags`, `msg_id`, `t_mono`, `field_count`, bounded `fields`.
- `core_log_field`: numeric `key_id`, typed value (`u32/u64/bool/msg_id/hash64/path_rel/path_redacted`).
- `msg_id` is a stable canonical token from the R-2 catalog; it is not localized text.

## Routing
Routing is done via `core_log_scope`:
- `CORE_LOG_SCOPE_GLOBAL`: `logs/rolling/events_rolling.tlv`
- `CORE_LOG_SCOPE_INSTANCE`: `instances/<id>/logs/rolling/events_rolling.tlv`
- `CORE_LOG_SCOPE_RUN`: `instances/<id>/logs/runs/<run_id>/events.tlv`

Launcher services provide the default sink. Setup frontends should write to a deterministic, per-run or per-session log under the setup state root.

## Determinism + Redaction
- All fields are numeric, bounded, and emitted in a stable order.
- No locale text, no `strerror`, no user or machine identifiers by default.
- Paths must be redacted unless they are safely relative to a known root.
- Use `core_log_path_make_relative()`; emit `PATH_REDACTED` if the path is outside the root.

## Extending the Schema
- `core_log_field_key`, `core_log_operation_id`, and `core_log_event_code` are append-only.
- Do not renumber existing values.
- Add new keys to this document and to the R-2 message catalog if they map to user-visible messages.

## Field Keys (Catalog)
The authoritative catalog lives in `include/dominium/core_log.h`. Common keys include:
- `CORE_LOG_KEY_OPERATION_ID`
- `CORE_LOG_KEY_RUN_ID`
- `CORE_LOG_KEY_STATUS_CODE`
- `CORE_LOG_KEY_ERR_DOMAIN` / `CORE_LOG_KEY_ERR_CODE` / `CORE_LOG_KEY_ERR_FLAGS` / `CORE_LOG_KEY_ERR_MSG_ID`
- `CORE_LOG_KEY_REFUSAL_CODE`
- `CORE_LOG_KEY_PATH`