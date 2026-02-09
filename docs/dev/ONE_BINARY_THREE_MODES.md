Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# One Binary Three Modes

## Scope

This document defines operator-visible behavior for binaries that expose
`cli`, `tui`, and `gui` modes through a single canonical command surface.

## Runtime Contract

- Mode registry: `data/registries/mode_backend.json`.
- Mode schema: `schema/ui/mode_backend.schema`.
- Launcher resolves mode by:
  1. explicit `--mode` argument,
  2. registry fallback order for platform/arch/abi,
  3. deterministic refusal if no compatible mode exists.

## Deterministic Selection

- Input tuple: `(platform, arch, abi, requested_mode, tty_present, backend_caps)`.
- Output: selected mode or refusal code.
- No wall-clock, random, or host-local mutable state in mode selection.

## Required Refusal Semantics

- `refuse.mode.invalid`
- `refuse.mode.backend_missing`
- `refuse.mode.entitlement_missing`
- `refuse.mode.environment_incompatible`

Each refusal must include mode id and backend id in details.

## Security And Governance

- Mode selection must not grant capabilities.
- GUI console dispatch must use canonical command dispatcher.
- RepoX enforces registry-driven backend selection.
- TestX validates mode fallback and refusal determinism.
