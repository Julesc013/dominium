Status: CANONICAL
Last Reviewed: 2026-01-29
Supersedes: none
Superseded By: none
STATUS: CANONICAL
OWNER: architecture
LAST_VERIFIED: 2026-01-29

# UI Binding Model (APP-UI-BIND-0)

This document is the canonical representation of PROMPT APP-UI-BIND-0.

Normative rules:
- UI_BIND_PHASE is mandatory for any GUI build and must run in CI/TestX.
- UI elements bind only to canonical command IDs via generated binding tables.
- UI code may only dispatch commands; no direct behavior, filesystem, or network logic.
- Accessibility and localization metadata are mandatory and validated at build time.
- CLI/TUI/GUI parity is enforced by tests; no UI-only actions are allowed.
