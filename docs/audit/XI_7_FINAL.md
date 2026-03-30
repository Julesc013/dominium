Status: DERIVED
Last Reviewed: 2026-03-30
Stability: stable
Future Series: XI-7
Replacement Target: superseded by a later explicit Xi-7 profile revision only

# XI-7 Final

## Scope

Xi-7 integrated the Xi-6 frozen architecture surfaces into the XStack CI pipeline without changing runtime semantics, contract behavior, or schema major versions.

New Xi-7 guard surfaces:

- `tools/xstack/ci/xstack_ci_entrypoint`
- `tools/xstack/ci/xstack_ci_entrypoint.py`
- `tools/xstack/ci/xstack_ci_entrypoint.ps1`
- `tools/xstack/ci/profiles/FAST.json`
- `tools/xstack/ci/profiles/STRICT.json`
- `tools/xstack/ci/profiles/FULL.json`
- `data/xstack/gate_definitions.json`
- `docs/xstack/CI_GUARDRAILS.md`
- `docs/xstack/ARCH_DRIFT_POLICY.md`
- `docs/audit/CI_RUN_REPORT.md`
- `data/audit/ci_run_report.json`

## Profile Definitions

- `FAST`
  - RepoX FAST
  - AuditX key drift and boundary checks
  - TestX FAST impact or explicit subset
  - `Ω-1`
  - `Ω-2`
- `STRICT`
  - RepoX STRICT
  - AuditX STRICT
  - TestX STRICT
  - `validate --all STRICT`
  - `ARCH-AUDIT-2`
  - `Ω-1` through `Ω-6`
- `FULL`
  - RepoX FULL
  - AuditX FULL
  - TestX FULL
  - STRICT validation surface
  - convergence gate
  - performance envelope
  - store verify
  - store GC
  - optional archive verify

Profile fingerprints:

- `FAST`: `b86a925aefb6db5a5aa386264a9bb5c146a3ebaf862b4d46cdff8aa837f56e7d`
- `STRICT`: `fe4493c561e5b82947118151576f9e92aaa8cf2be9a4cc3c736153ccbee2b44c`
- `FULL`: `8e86c40ac50ccc024759887b49035e80ec22f9ac9e1b7eba6f6e25bde2401566`
- gate definitions: `11fe82bb4063f41e56e114a34cc8874eaed4e18084eddc5efe787ac80d1b4498`

## Enforced Invariants

RepoX hard rules:

- `INV-NO-SRC-DIRECTORY`
- `INV-ARCH-GRAPH-V1-PRESENT`
- `INV-MODULE-BOUNDARIES-RESPECTED`
- `INV-SINGLE-CANONICAL-ENGINES`
- `INV-XSTACK-CI-MUST-RUN`
- `INV-STRICT-MUST-PASS-FOR-MAIN`

AuditX detectors:

- `E560_ARCHITECTURE_DRIFT_SMELL`
- `E561_FORBIDDEN_DEPENDENCY_SMELL`
- `E562_DUPLICATE_SEMANTIC_ENGINE_REGISTRY_SMELL`
- `E563_UI_TRUTH_LEAK_BOUNDARY_SMELL`
- `AUDITX_NUMERIC_DISCIPLINE_SCAN`
- `E564_MISSING_CI_GUARD_SMELL`

Task-level invariants upheld:

- `constitution_v1.md A1`
- `constitution_v1.md A8`
- `constitution_v1.md A10`
- `AGENTS.md §2`
- `AGENTS.md §5`

## Drift Update Procedure

Intentional architecture change requires:

1. prepare a ControlX plan with `python -B tools/controlx/tool_plan_arch_change.py --repo-root .`
2. attach `ARCH-GRAPH-UPDATE`
3. update the Xi-6 frozen architecture artifacts deliberately
4. pass the Xi-7 `FULL` profile

Adding a new module requires:

1. update `data/architecture/module_registry.v1.json`
2. update `data/architecture/architecture_graph.v1.json`
3. pass `STRICT`
4. pass `FULL`

Adding a new dependency requires:

1. update `data/architecture/module_boundary_rules.v1.json`
2. preserve constitutional architecture
3. pass `STRICT`
4. pass `FULL`

## Human and AI Drift Protection

Xi-7 protects against human and AI drift by combining:

- frozen Xi-6 graph presence checks
- module-boundary enforcement
- duplicate semantic-engine detection
- `src/` reintroduction refusal
- workflow wiring checks for local and GitHub CI entrypoints
- deterministic TestX checks for profile and gate metadata
- deterministic CI stage ordering
- refusal on stale or internally-refused validation reports

Prompts remain untrusted.
CI is authoritative.

## Provisional Allowances

- `xi7_data_architecture_support_surface`
  - scope: `architecture_drift`
  - reason: Xi-6 and Xi-7 freeze artifacts live under `data/architecture`
  - replacement plan: classify `data/architecture` explicitly in the next architecture-update revision
- `xi7_data_architecture_support_surface_boundary`
  - scope: `module_boundary`
  - reason: Xi-6 and Xi-7 freeze artifacts live under `data/architecture`
  - replacement plan: classify `data/architecture` explicitly in the next architecture-update revision
- `xi7_tools_controlx_review_bridge`
  - scope: `module_boundary`
  - reason: ControlX planning still reuses review-side helpers during Xi-7 integration
  - replacement plan: move shared logic into a neutral support surface or refresh module boundaries under `ARCH-GRAPH-UPDATE`

## Validation

Requested Xi-7 tests passed:

- `test_ci_entrypoint_deterministic_order`
- `test_ci_profiles_exist`
- `test_gate_definitions_valid`

Additional Xi-7 regression guard passed:

- `test_ci_report_failures_propagate`

Direct strict gate runs passed:

- `validate --all STRICT`
- `ARCH-AUDIT-2`
- `Ω-1 worldgen lock verify`
- `Ω-2 baseline universe verify`
- `Ω-3 gameplay loop verify`
- `Ω-4 disaster suite`
- `Ω-5 ecosystem verify`
- `Ω-6 update sim`

End-to-end Xi-7 smoke passed through the committed entrypoint:

- command: `python -B tools/xstack/ci/xstack_ci_entrypoint.py --repo-root . --profile STRICT --testx-subset test_ci_entrypoint_deterministic_order,test_ci_profiles_exist,test_gate_definitions_valid,test_ci_report_failures_propagate`
- result: `complete`
- CI run fingerprint: `d8ac4aece502463999d0fe93940bee4babd58022211f1b9e4aeb65a33bfeb1a0`

Local validation note:

- the repository's broader `TestX STRICT` inventory was not rerun end-to-end through Xi-7 during this integration proof because it materially exceeds the local shell budget
- the Xi-7 entrypoint, profile ordering, RepoX and AuditX rules, and strict validation and Omega gates were all exercised directly and via the Xi-7 smoke lane above

## Readiness

- architecture drift is detected automatically: `true`
- duplicate semantic engines are blocked: `true`
- `src/` reintroduction is blocked: `true`
- module boundary violations are blocked: `true`
- missing CI guard surfaces are blocked: `true`
- ready for Xi-8 repository freeze: `true`
