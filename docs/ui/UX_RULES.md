# UX Rules (UX-2)

Status: binding.
Scope: global UX rules for CLI/TUI/GUI across setup, launcher, client, and tools.

## Canonical rules
- CLI is canonical for commands, flags, and refusal semantics.
- TUI and GUI are projections of CLI semantics and use the same intent handlers.
- No UI-only behavior is allowed.
- Refusals are always visible and explainable (code_id, code, message, details).
- Missing content is explained, never hidden.
- Debug and inspect features are discoverable but non-intrusive.

## Operational rules
- UI surfaces are presentation-only by default and must not mutate state directly.
- Any mutation path must be an admitted Process with law/refusal gates.
- Compatibility mode must be visible (full/degraded/frozen/inspect-only/refuse).
- UI may suggest actions but must not auto-correct or auto-execute intent.

## Sentinel tags (do not remove)
- UX-PARITY-CLI-CANON
- UX-PARITY-NO-UI-ONLY
- UX-REFUSAL-VISIBLE
- UX-MISSING-CONTENT-EXPLAINED
- UX-DEBUG-DISCOVERABLE

