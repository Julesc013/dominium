Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# PROFILE_OVERRIDE_BASELINE

Status: BASELINE (`META-PROFILE-0`)  
Last Reviewed: 2026-03-07  
Version: 1.0.0  
Scope: unified profile override architecture with deterministic profile resolution and canonical exception ledger events.

## Profile Types

Implemented profile categories (`schema/meta/profile.schema`, `data/registries/profile_registry.json`):

- `physics`
- `law`
- `process`
- `safety`
- `epistemic`
- `coupling`
- `compute`

Seed registry profile IDs:

- `physics.default_realistic`
- `physics.alternate_magic`
- `law.softcore`
- `law.strict`
- `process.default`
- `process.strict`
- `safety.default`
- `epistemic.default_diegetic`
- `epistemic.admin_full`
- `coupling.default`
- `compute.default`

## Binding Resolution Order

Deterministic override resolution is implemented by `resolve_profile(...)` in `src/meta/profile/profile_engine.py` with stable precedence:

1. `universe` baseline bindings (UniverseIdentity scope)
2. `session` bindings (SessionSpec scope)
3. `authority` bindings (AuthorityContext scope)
4. `system` bindings (SystemTemplate/owner scope)

Tie-breaking and normalization are deterministic by stable key ordering and canonical hashing.

## Exception Ledger Rules

When a profile override changes rule behavior, runtime must emit a canonical `exception_event` row (`schema/meta/exception_event.schema`) via `build_profile_exception_event_row(...)`.

Required fields:

- `event_id` (stable prefix: `event.profile.override.`)
- `profile_id`
- `rule_id`
- `owner_id`
- `tick`
- `details` (optional)
- `deterministic_fingerprint`

Integration points:

- `apply_override(...)` emits structured exception payloads
- `src/system/system_collapse_engine.py` appends deterministic profile exception rows into `profile_exception_events`

## Mode Flag Elimination Status

- Legacy mode-like token scanning is enforced via RepoX invariant `INV-NO-MODE-FLAGS`.
- Profile-based overrides are enforced via:
  - `INV-OVERRIDE-REQUIRES-PROFILE`
  - `INV-EXCEPTION-EVENT-LOGGED`
- AuditX support:
  - `ModeFlagSmell`
  - `SilentOverrideSmell` (`E304_SILENT_OVERRIDE_SMELL`)

## Gate Snapshot

Executed during META-PROFILE-0 finalization:

- RepoX STRICT: `refusal` (repository-level pre-existing blockers outside META-PROFILE-0 scope remain, including worktree hygiene and prior cross-series hard-fails).
  - Command: `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
- TestX FAST subset (topology coverage): `pass`
  - Command: `python tools/xstack/testx/runner.py --profile FAST --subset test_topology_map_includes_all_schemas,test_topology_map_includes_all_registries`
- META-PROFILE invariant cases: `pass`
  - Command: `python tests/invariant/profile_override_architecture_tests.py --case ...` (all 5 cases)
- strict build: not rerun in this pass due existing repository-level STRICT gate refusals.

## Readiness

META-PROFILE-0 contract surfaces are in place:

- profile + binding + exception schemas/registry
- deterministic runtime resolution engine
- session/authority integration
- mode-flag replacement path wired for SYS collapse guard path
- RepoX/AuditX/TestX coverage added

Ready for `META-COMPUTE-0` and `LOGIC-0` profile-driven budget/governance extensions.
