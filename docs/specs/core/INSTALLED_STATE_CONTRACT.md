Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Installed State Contract (Setup -> Launcher)

`installed_state.tlv` is the deterministic, versioned record produced by setup
and consumed by launcher core. It contains the selected splat, installed
components, install roots, and artifact inventory needed for audit and
verification.

## Scope

- Kernel-only: no OS/UI dependencies.
- Deterministic: stable ordering, canonical TLV encoding, skip-unknown.
- No user-facing strings; errors use `err_t` + msg_id at the edges.

## Schema Summary

The schema is defined in `include/dominium/core_installed_state.h` and documented
in `docs/setup/TLV_INSTALLED_STATE.md`.

Required root fields:
- product id
- installed version
- selected splat id
- install scope
- install root (primary)
- manifest digest64
- request digest64

Optional root fields:
- install roots list
- ownership model
- artifacts list
- registrations list
- previous_state_digest64

## Location and Handoff

Setup frontends write `installed_state.tlv` to the path they control (via
`--out-state` or equivalent). The launcher core parses the file via
`launcher_installed_state_from_tlv_bytes` and may compute a stable hash for audit.

The contract is path-agnostic; orchestration decides how to pass the state path
to the launcher (e.g., an explicit CLI flag or a deterministic config field).

## Determinism Rules

- Root tags are canonicalized by value order where applicable.
- Lists are sorted deterministically (see schema doc).
- No locale text, timestamps, or OS-specific path expansions in the payload.