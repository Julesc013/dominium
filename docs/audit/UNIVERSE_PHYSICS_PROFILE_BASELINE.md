Status: DERIVED
Last Reviewed: 2026-02-26
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: RS-1 baseline; bound to canon and schema v1.0.0 contracts.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# UniversePhysicsProfile Baseline

## Scope
RS-1 establishes immutable `UniversePhysicsProfile` selection, deterministic null boot with zero packs, and profile compatibility checks in save/session/network flows.

## Null Profile Definition
- Built-in profile id: `physics.null`
- Domain bindings: `enabled_domain_ids = []`
- Conservation set: `none`
- Exception types: `[]`
- Numeric precision policy: `default_null`
- Tier taxonomy: `default_minimal`
- Time model: `default_single_tick`
- Boundary model: `procedural_infinite`
- Error budget: empty object

Null boot writes deterministic lockfile + registries via `write_null_boot_artifacts(...)` and supports tick execution with no assemblies.

## Realistic Default Pack Definition
- Optional pack: `packs/physics/physics.default.realistic`
- Contribution type: `registry_entries`
- Contributed profile id: `physics.default.realistic`
- Runtime behavior:
  - profile is selectable only if present in compiled registry outputs
  - removal does not break runtime; fallback remains `physics.null` unless explicitly requesting another available profile

## Immutability Guarantees
- `UniverseIdentity` includes required `physics_profile_id`.
- `physics_profile_id` participates in deterministic identity hash.
- Mid-lineage profile mutation is refused:
  - `refusal.physics_profile_missing` when requested/declared profile is unavailable
  - `refusal.physics_profile_mismatch` on client/server/save lineage mismatch
- Runtime compares current identity profile against previous run-meta lineage profile to enforce immutability.

## Multiplayer Handshake Integration
- Handshake request/response extensions carry physics profile ids.
- Server enforces compatibility before session accept.
- Client never negotiates alternate physics profile at runtime; mismatch is a deterministic refusal.

## RepoX/AuditX Guardrails
- RepoX invariants:
  - `INV-NO-HARDCODED-PHYSICS-ASSUMPTIONS`
  - `INV-PHYSICS-PROFILE-IN-IDENTITY`
- AuditX analyzers:
  - `PhysicsAssumptionSmell` (`E40_PHYSICS_ASSUMPTION_SMELL`)
  - `ImplicitDefaultProfileSmell` (`E41_IMPLICIT_DEFAULT_PROFILE_SMELL`)

## TestX Coverage (RS-1)
- `test_null_boot_deterministic`
- `test_default_profile_optional`
- `test_physics_profile_immutable`
- `test_save_contains_physics_profile_id`

## Gate Results
- RepoX: PASS
  - `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
- AuditX: run complete
  - `py -3 tools/auditx/auditx.py verify --repo-root . --format both`
- TestX: RS-1 coverage PASS
  - `py -3 tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset testx.reality.null_boot_deterministic,testx.reality.default_profile_optional,testx.reality.physics_profile_immutable,testx.reality.save_contains_physics_profile_id`
  - Additional impacted compile/import tests PASS:
    `testx.registry.compile`, `testx.lockfile.validate`, `testx.ui.registry.determinism`, `testx.data.derived_hash_changes_on_source_change`, `testx.data.spice_import_determinism`, `testx.data.srtm_import_determinism`
- strict build: PASS
  - `py -3 tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.rs1 --cache on --format json`
- ui_bind --check: PASS
  - `py -3 tools/xstack/ui_bind.py --repo-root . --check`

## Known Non-RS Strict Profile Findings
- Full strict profile execution (`py -3 tools/xstack/run.py strict --repo-root . --cache on`) remains non-pass due pre-existing/non-RS baseline failures in:
  - envelope full-stack determinism test,
  - regression baseline hash locks,
  - negative-invariant smoke expectations,
  - strict profile aggregate run smoke wrapper.
- These do not block RS-1 profile architecture, null boot, or physics profile immutability coverage.

## Known Extension Points (RS-2+)
- Conservation contract enforcement policy (`conservation_contract_set_id`) remains declarative in RS-1.
- Tier collapse/expand invariant enforcement remains profile-linked; heavy conservation checks are deferred to RS-2.
- Additional physics packs can contribute new `UniversePhysicsProfile` rows through pack registries without runtime branching.
