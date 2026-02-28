Status: DRAFT
Version: 1.0.0

# Adapter Pattern

## Purpose
Adapters allow deterministic, incremental migration from deprecated interfaces to canonical substrates without changing simulation semantics.

## Rules
- Adapter direction is one-way: old interface -> new canonical implementation.
- Adapters must not introduce new behavior.
- Adapters must preserve deterministic ordering and refusal semantics.
- Adapters must be temporary and listed in `data/governance/deprecations.json`.

## Required Adapter Structure
- Old surface contract (input shape and validation)
- Canonical mapping logic
- New substrate call path
- Output normalization to legacy shape (if required)
- No hidden writes and no direct truth mutation

## Registration
- Each adapter path must appear in a deprecation entry:
  - `deprecated_id`
  - `replacement_id`
  - `adapter_path`
  - `status`

## Allowed Adapter Access
- Adapter files explicitly listed in `data/governance/deprecations.json` may reference `legacy/` or `quarantine/`.
- All other paths are refused by enforcement.

## Removal
- When compatibility is no longer needed:
  - mark entry `removed`
  - delete adapter
  - verify removed identifier has zero references via governance checks

