Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Version: 1.0.0
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Deprecation Lifecycle

## Purpose
Deprecation exists to enable deterministic, auditable migration from old contracts to canonical replacements without silent drift, forked behavior, or runtime contamination.

## Lifecycle States
- `active`
- `deprecated`
- `quarantined`
- `removed`

### State Meaning
- `active`: Item is still supported and not scheduled for immediate removal.
- `deprecated`: Item is still readable/usable for compatibility only and has a declared replacement.
- `quarantined`: Item is isolated from production runtime paths and may be reached only through declared adapters.
- `removed`: Item is no longer supported and must not be referenced by runtime or tool contracts except historical audit artifacts.

## Mandatory Rules
- Every deprecated item must declare:
  - `replacement_id`
  - `reason`
  - `removal_target_version`
- New code must not introduce fresh references to deprecated identifiers.
- Quarantined code must not be linked into runtime targets.
- Any temporary compatibility route must use a declared adapter and be registered.

## Adapter Contract
- Adapter shells map an old interface to a new canonical substrate.
- Adapters are temporary migration bridges, not permanent facades.
- Adapter usage must be declared in `data/governance/deprecations.json` via `adapter_path`.
- Adapters must be deterministic and side-effect free except for canonical process dispatch.

## Quarantine Policy
- `legacy/` and `quarantine/` are non-production zones.
- Production runtime modules (`src/`, `engine/`, `game/`, `client/`, `server/`, `platform/`) must not import from these directories.
- Adapter-only references are allowed only from explicitly declared adapter paths.

## Governance and Enforcement
- RepoX enforces:
  - `INV-DEPRECATION-REGISTRY-VALID`
  - `INV-NO-NEW-USE-OF-DEPRECATED`
  - `INV-ADAPTER-ONLY-ACCESS`
  - `INV-NO-PRODUCTION-LEGACY-IMPORT`
- AuditX reports semantic drift and missing adapter coverage.
- TestX validates deterministic deprecation artifacts and quarantine boundaries.

## Determinism and Replay
- Deprecation metadata is governance-only and does not alter simulation semantics.
- Migration/adaptation paths must preserve deterministic outcomes for equal inputs.
- No wall-clock based behavior is introduced by deprecation tooling.
