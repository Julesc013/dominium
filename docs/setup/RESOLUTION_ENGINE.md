# Setup Core Resolution Engine (Plan S-3)

This document specifies the deterministic, OS-agnostic component resolution layer added in Plan S-3.
The resolver converts a validated manifest + user intent + (optional) installed state into a closed, canonical **resolved set**. It performs no filesystem mutation.

## Inputs

### 1) Manifest (`*.dsumanifest`)

Input manifest must already be:
- syntactically valid
- validated
- canonicalized (stable ordering + normalization)

See `docs/setup/MANIFEST_SCHEMA.md`.

### 2) User request (`dsu_resolve_request_t`)

Fields (public ABI):
- `operation`: `install | upgrade | repair | uninstall`
- `requested_components[]`: explicit selections (component IDs; mixed-case allowed; normalized to lowercase ASCII IDs)
- `excluded_components[]`: explicit exclusions (component IDs; normalized)
- `scope`: `portable | user | system`
- `target_platform`: optional platform triple
  - if the manifest has **exactly one** platform target and `target_platform` is empty, that single target is used
  - if the manifest has **multiple** platform targets and `target_platform` is empty, resolution fails with `invalid_request` (no silent choice)
- `allow_prerelease`: if `no`, selecting any pre-release version fails with `version_conflict`
- `pins[]`: optional version pinning rules (minimal in S-3)
  - pin = `(component_id, version)` and must match the resolved version exactly, otherwise `version_conflict`

### 3) Installed state (`dsu_state_t`, optional)

Loaded via `dsu_state_load_file()`. Used only in Phase 5 to reconcile install/upgrade/repair/uninstall semantics.

## Outputs

### Resolved set (`dsu_resolve_result_t`)

The result contains:
- `operation`, `scope`, `platform`
- `product_id`, `product_version`, `install_root` (resolved install root for `(platform, scope)`)
- `manifest_digest64` (from the canonical manifest TLV payload)
- `resolved_digest64` (u64 digest of the canonical resolved set)
- `resolved_components[]` sorted lexicographically by `component_id`:
  - `component_id`
  - `resolved_version`
  - `source`: `default | user | dependency | installed`
  - `action`: `none | install | upgrade | repair | uninstall`
- `resolution_log[]`: structured deterministic events (no timestamps)

### Failure model (no partial results)

Resolution fails fast with explicit status codes:
- `missing_component`: user requested a component not present in manifest
- `unsatisfied_dependency`: required dependency cannot be satisfied
- `version_conflict`: version constraint/pin/prerelease rule violated
- `explicit_conflict`: selected components conflict
- `platform_incompatible`: requested platform/scope has no compatible install root (or platform not supported)
- `illegal_downgrade`: upgrade would downgrade an installed component
- `invalid_request`: malformed request or ambiguous required inputs (e.g., missing platform with multiple manifest targets)

On failure, the resolver does not mutate state and does not emit a partial resolved set.

## Determinism guarantees

The resolver is fully deterministic:
- No recursion without explicit ordering.
- No pointer-address-based ordering.
- No iteration over unsorted containers.
- All ID comparisons are ASCII-only, bytewise lexicographic.
- Resolved components are always sorted by `component_id`.
- `resolved_digest64` is computed over stable inputs: `(platform, scope, component_id/version list)`.
- `resolution_log` event ordering is stable and derived from deterministic phases.

## Resolution phases

Resolution proceeds in fixed phases:

### Phase 1 — Seed selection

Seed set =
- explicit `requested_components`
- plus all manifest components flagged `default-selected` unless explicitly excluded

All IDs are normalized to lowercase ASCII IDs; duplicates are rejected deterministically.

### Phase 2 — Dependency closure

Iteratively add required dependencies until closure:
- constraint kinds: `any`, `exact`, `at_least`
- if a dependency cannot be satisfied, fail with `unsatisfied_dependency`
- if pins exist and disagree with selected versions, fail with `version_conflict`

No “best effort” choices are made.

### Phase 3 — Conflict detection

If any two selected components conflict, fail deterministically with `explicit_conflict` and emit a conflict log event.

No automatic conflict resolution is attempted.

### Phase 4 — Platform selection / filtering

Select the target platform (see request rules above) and resolve an install root for `(platform, scope)`.

If no compatible install root exists, fail with `platform_incompatible`.

### Phase 5 — Installed-state reconciliation

Operation semantics:

- **Install**
  - if any selected component is already installed, fail with `invalid_request` (no implicit upgrade)
  - resolved component actions are `install`

- **Upgrade**
  - selected components must be present in installed state, otherwise `invalid_request`
  - version monotonicity enforced:
    - installed `<` manifest ⇒ action `upgrade`
    - installed `==` manifest ⇒ action `none`
    - installed `>` manifest ⇒ `illegal_downgrade`

- **Repair**
  - selected components must be present in installed state, otherwise `invalid_request`
  - installed version must exactly match manifest, otherwise `invalid_request`
  - action `repair`

- **Uninstall**
  - resolution is restricted to installed components only
  - non-installed requested components are ignored (and logged)
  - action `uninstall`

### Phase 6 — Canonical ordering + digest

Finalize the resolved set:
- sort resolved components lexicographically by `component_id`
- compute `resolved_digest64`

## CLI examples

Resolve to JSON (stable ordering):

`dominium-setup resolve --manifest docs/setup/sample_manifest.dsumf --install --components launcher,runtime --scope portable --platform any-any --json`

Resolve against an installed-state snapshot:

`dominium-setup resolve --manifest manifest.dsumanifest --installed-state state.dsustate --upgrade --components launcher --scope user --platform win64-x64 --json`

