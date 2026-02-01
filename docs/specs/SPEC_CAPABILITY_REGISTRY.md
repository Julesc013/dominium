Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- None. Game consumes engine primitives where applicable.

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC_CAPABILITY_REGISTRY — Central Backend Registry (Authoritative)

This spec defines the centralized capability/selection registry used to
deterministically choose runtime backends across subsystems (platform/system,
graphics, etc.). It exists to make backend selection:
- deterministic (registration order is not trusted)
- inspectable (available vs selected backends are printable)
- enforceable (determinism grades and lockstep requirements)

Primary APIs:
- `include/domino/caps.h`
- `include/domino/profile.h`
- `include/domino/determinism.h`

## 1. Data model

### 1.1 Backend descriptor (`dom_backend_desc`)
Each backend registers a descriptor POD:
- ABI header: `abi_version`, `struct_size`
- subsystem identity: `subsystem_id` (stable numeric id) and optional `subsystem_name`
- backend identity: `backend_name` (stable ASCII id) and `backend_priority`
- eligibility: `required_hw_flags` (bitset checked against `dom_hw_caps`)
- determinism: `dom_det_grade determinism`
- performance class: `dom_caps_perf_class perf_class`
- policy flags:
  - `subsystem_flags` (e.g. `DOM_CAPS_SUBSYS_LOCKSTEP_RELEVANT`)
  - `backend_flags` (e.g. `DOM_CAPS_BACKEND_PRESENTATION_ONLY`)
- optional hooks:
  - `get_api(requested_abi)` returning a versioned ABI struct/vtable pointer
  - `probe(dom_hw_caps*)` for runtime capability discovery (no allocations)

### 1.2 Profile input (`dom_profile`)
Selection receives a launcher-produced `dom_profile` (POD, C ABI):
- `kind`: `compat`, `baseline`, `perf`
- `lockstep_strict`: 0/1
- optional backend preferences:
  - `preferred_gfx_backend`
  - `overrides[]` list (bounded)

## 2. Registry lifecycle

### 2.1 Registration
Backends register via:
- `dom_caps_register_backend(const dom_backend_desc*)`

Rules:
- compiled-out backends MUST NOT register
- duplicate `(subsystem_id, backend_name)` is rejected
- registration after finalization is rejected

### 2.2 Built-in registration
The engine provides a convenience entry point:
- `dom_caps_register_builtin_backends()`

It registers all built-in subsystems compiled into the binary (currently DSYS
and DGFX for this prompt).

### 2.3 Finalization
Before selection, the registry is finalized:
- `dom_caps_finalize_registry()`

Finalization:
- sorts registered backends deterministically
- locks the registry against further registration

## 3. Deterministic ordering rules

Registry ordering MUST be deterministic and MUST NOT depend on caller
registration order.

Current ordering key:
1. `subsystem_id` ascending
2. `backend_priority` descending (higher is preferred)
3. `backend_name` case-insensitive ascending (stable tiebreak)

## 4. Selection rules

Selection API:
- `dom_caps_select(profile, hw, out_selection)`

### 4.1 Eligibility
A backend is eligible when:
- hardware requirements are satisfied (`required_hw_flags`)
- any profile-driven policy constraints are satisfied

If `hw` is `NULL`, selection treats hardware as unknown and only allows
backends with `required_hw_flags == 0`.

### 4.2 Profile kind (compat/baseline/perf)
Within a subsystem, eligible backends are scored by profile kind:
- `baseline`: prefer `baseline`, then `compat`, then `perf`
- `compat`: prefer `compat`, then `baseline`, then `perf`
- `perf`: prefer `perf`, then `baseline`, then `compat`

Ties are broken by `backend_priority` and then `backend_name` to keep selection
deterministic.

### 4.3 Explicit backend preferences
If the profile specifies a backend preference for a subsystem:
- the selection MUST attempt to select that backend
- if the backend is not present, selection fails with a structured reason
- if the backend is present but ineligible, selection fails with a structured reason

### 4.4 Lockstep strict determinism enforcement
If `profile.lockstep_strict == 1`:
- subsystems marked `DOM_CAPS_SUBSYS_LOCKSTEP_RELEVANT` MUST select a `D0` backend
- selection MUST NOT silently downgrade a lockstep-relevant subsystem to `D1/D2`
- if no eligible `D0` backend exists, selection fails explicitly

Renderer and other presentation subsystems are typically not lockstep-relevant;
they may remain `D2` provided they cannot influence authoritative simulation.

## 5. Audit log

Selection results can be rendered as a stable text log:
- `dom_caps_get_audit_log(selection, buf, io_len)`

The log is intended for `--print-selection` output and includes:
- selected backend per subsystem
- determinism grade, perf class, and priority
- selection reason (`priority` vs `override`)