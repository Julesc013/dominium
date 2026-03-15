Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: COMPAT/RELEASE
Replacement Target: migration-policy-governed artifact loaders and release-pinned migration governance

# MIGRATION-LIFECYCLE-0 Retro Audit

## Existing Surfaces

- `src/compat/data_format_loader.py`
  - already performs deterministic artifact-version loading for `save_file`, `blueprint_file`, `profile_bundle`, `session_template`, and `pack_lock`
  - already applies deterministic migration chains from `data/registries/migration_registry.json`
  - already supports explicit read-only fallback for future versions
- `src/lib/save/save_validator.py`
  - already normalizes `save_format_version`
  - already supports deterministic `migration_chain` rows and read-only open decisions
  - save migration logic is currently local to the save validator instead of policy-driven
- `src/lib/install/install_validator.py`
  - validates install manifests deterministically
  - currently has no explicit migration policy consultation
- `src/lib/instance/instance_validator.py`
  - validates instance manifests deterministically
  - currently has no explicit migration policy consultation
- `src/release/release_manifest_engine.py`
  - canonicalizes release manifests with `manifest_version`
  - does not currently expose migration-policy decisions
- `src/release/update_resolver.py`
  - canonicalizes release indices and install plans
  - no shared migration lifecycle policy is consulted during load

## Current Version Fields

- `save.manifest.json`
  - `save_format_version`
  - mirrored to `format_version`
- PACK-COMPAT-2 generic artifacts
  - `format_version`
- release manifest
  - `manifest_version`
- negotiation record
  - `schema_version`
- install manifest / instance manifest / release index / component graph / install plan
  - no dedicated migration lifecycle field yet; current loaders implicitly assume current schema semantics

## Existing Migration Registry Usage

- `data/registries/migration_registry.json`
  - used by `src/compat/data_format_loader.py`
  - keyed by legacy `component_type`
  - deterministic migration chain exists for:
    - blueprint
    - pack_lock
    - profile
    - save
    - session_template

## Existing Read-Only Behavior

- generic PACK-COMPAT-2 loader:
  - future version can open read-only if explicitly allowed and structurally safe
- save validator:
  - read-only allowed only when `allow_read_only_open` is true and instance/tool mode permits it
  - contract / pack-lock / build mismatches degrade to read-only only when allowed
- install / instance / release artifacts:
  - no shared read-only lifecycle policy currently exists

## Ad Hoc / Missing Lifecycle Governance

- install manifests and instance manifests currently validate directly without consulting a migration policy registry
- release index, component graph, and install plan canonicalizers assume current semantics without emitting a migration decision record
- migration tooling exists only for PACK-COMPAT-2 replay and save migration helpers; there is no universal migration planner/apply surface
- no single canonical migration decision record currently spans:
  - migrate
  - direct load
  - read-only
  - refuse

## Required MIGRATION-LIFECYCLE-0 Outcome

- freeze policy per artifact class
- preserve existing deterministic migration behavior
- make read-only and refusal decisions explicit and reportable
- forbid silent migrations and policy-free loads going forward
