Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Data Format Compatibility Baseline

## Scope
PACK-COMPAT-2 establishes deterministic format metadata and migration hooks for persistent artifact loading.

## Artifact Version Matrix
- `save_file`
  - current format: `2.0.0`
  - legacy fallback: `1.0.0`
  - semantic contract pin: required
- `blueprint_file`
  - current format: `2.0.0`
  - legacy fallback: `1.0.0`
  - required contract ranges: optional
- `profile_bundle`
  - current format: `2.0.0`
  - legacy fallback: `1.0.0`
- `session_template`
  - current format: `2.0.0`
  - legacy fallback: `1.0.0`
- `pack_lock`
  - current format: `2.0.0`
  - legacy fallback: `1.0.0`

## Migration Registry Summary
- `migration.save.v1_to_v2`
- `migration.blueprint.v1_to_v2`
- `migration.profile.v1_to_v2`
- `migration.session_template.v1_to_v2`
- `migration.pack_lock.v1_to_v2`

All baseline migrations are deterministic metadata migrations that:
- stamp `format_version`
- stamp `engine_version_created`
- preserve or inject contract-bound metadata where required
- log migration history and migration events

## Read-Only Fallback Rules
- Future-format artifacts may open read-only only when the caller explicitly allows it.
- Read-only fallback binds `law.observer.default`.
- Mutation-capable loaders refuse future-format artifacts when migration is unavailable.

## Proof / Replay
- Migration events are emitted deterministically by the shared loader.
- Replay tooling re-runs the migration chain and verifies identical post-migration fingerprints.

## Known Intentional Limits
- No automatic migration is performed without explicit logging.
- No pack contents are rewritten in place.
- No online migration catalog is required.

## Readiness
This baseline prepares persistent artifact loading for:
- portable Setup / Launcher flows
- supervised local singleplayer
- future APPSHELL orchestration
- final MVP gatekeeping without silent artifact reinterpretation
