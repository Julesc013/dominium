# SPEC_SYS_CAPS (HWCAPS0)

Schema ID: SYS_CAPS
Schema Version: 1.0.0
Status: binding.
Scope: hardware/platform capability descriptor used by execution policy.

## Purpose
Define a conservative, versioned SysCaps payload for deterministic backend
selection and budget derivation. SysCaps influence performance policy only;
they never change gameplay meaning.

## Core Rules
- Unknown values are permitted and must be treated conservatively.
- No benchmarking or wall-clock measurements are allowed.
- SysCaps are inputs to execution policy only; they never affect gameplay state.
- All downgrades triggered by SysCaps must be auditable.
- GPU compute is DERIVED-only unless explicitly proven strict (not in HWCAPS0).

## Versioning
- SysCaps are versioned by `version_major` and `version_minor`.
- Minor bumps may add fields; unknown fields must be ignored safely.
- Major bumps may redefine semantics and require migration notes.
- Changes must follow `schema/SCHEMA_VERSIONING.md`.

## Serialization
SysCaps are serialized and hashed deterministically. See
`SPEC_SYS_CAPS_FIELDS.md` for canonical field ordering and `docs/specs/`
container requirements when stored on disk.
