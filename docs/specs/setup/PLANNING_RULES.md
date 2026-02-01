Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Planning Rules (SR-4)

## Deterministic resolution
1. Seed selection
   - If `requested_components` is provided, seed with those.
   - Else seed with `default_selected` components.
   - Apply exclusions; if a requested component is missing, refuse.
2. Dependency closure
   - Add deps until fixed point.
   - Missing deps or excluded deps => refuse `UNSATISFIED_DEPENDENCY`.
3. Conflict detection
   - If any selected pair conflicts => refuse `EXPLICIT_CONFLICT`.
4. Platform filtering
   - If a selected component has `supported_targets` and the request platform is not included:
     - If user-requested => refuse `PLATFORM_INCOMPATIBLE`.
     - If required by another component => refuse `PLATFORM_INCOMPATIBLE`.
     - Otherwise remove it from the resolved set.
5. Canonical ordering
   - Sort resolved components by `component_id`.
   - Resolve `component_version` to explicit value (component override or product version).

## Refusal codes
- `COMPONENT_NOT_FOUND` (unknown component id)
- `UNSATISFIED_DEPENDENCY` (missing dep or excluded dep)
- `EXPLICIT_CONFLICT` (conflicting selection)
- `PLATFORM_INCOMPATIBLE` (requested or required component unsupported)
- `INVALID_REQUEST` (reserved)
- `ARTIFACT_MISSING_DIGEST` (reserved)

## Digests
- `resolved_set_digest64` is FNV-1a over `component_id + 0x00 + component_version + 0x00` in canonical order.
- `plan_digest64` is FNV-1a over the plan TLV payload with `plan_digest64` set to `0` during hashing.

## Non-goals in SR-4
- No version range solving.
- No heuristic scoring or auto conflict resolution.
- No execution, filesystem mutation, or job DAG execution.