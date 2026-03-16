Status: DERIVED
Last Reviewed: 2026-02-28
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: CTRL-0 Control Plane Constitution baseline.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Control Plane Constitution Baseline

## Constitution Summary
- Added canonical control-plane constitution: `docs/control/CONTROL_PLANE_CONSTITUTION.md`.
- Defined the single control gateway contract:
  - `ControlIntent -> (optional Control IR) -> ControlPolicy resolution -> IntentEnvelope(s)/Commitments -> Processes`.
- Frozen AL0-AL4 abstraction levels and deterministic downgrade behavior.
- Frozen no-mode-flag rule for control behavior; policy and authority context drive behavior.
- Frozen planning/execution separation:
  - planning is derived-only,
  - execution is commitment/event/process-driven.
- Frozen replay/reenactment non-mutation rule.

## Retro-Audit Summary
- Retro consistency audit produced in `docs/audit/CTRL0_RETRO_AUDIT.md`.
- Key findings identified for migration:
  - direct envelope/intent dispatch points outside planned control module paths,
  - ad-hoc camera/occlusion bypass path,
  - admin override path missing explicit meta-law exception coupling,
  - duplicate control-like dispatch paths across interaction/tooling surfaces.
- Each finding includes target replacement and deprecation tracking requirement.

## Reason and Refusal Code Updates
- Added control-plane refusal/downgrade codes in `docs/contracts/refusal_contract.md`:
  - `refusal.ctrl.forbidden_by_law`
  - `refusal.ctrl.entitlement_missing`
  - `refusal.ctrl.view_forbidden`
  - `refusal.ctrl.fidelity_denied`
  - `refusal.ctrl.planning_only`
  - `refusal.ctrl.meta_forbidden`
  - `refusal.ctrl.replay_mutation_forbidden`
  - `refusal.ctrl.degraded` (downgrade marker)
  - `downgrade.budget_insufficient`
  - `downgrade.rank_fairness`
  - `downgrade.epistemic_limits`
  - `downgrade.policy_disallows`
  - `downgrade.target_not_available`

## Deprecation and Enforcement Preparation
- Added migration-target deprecations in `data/governance/deprecations.json` for:
  - interaction dispatch direct envelope construction/execution sites,
  - tool-side command dispatch construction,
  - ad-hoc freecam/occlusion bypass path,
  - legacy admin override path,
  - SRZ/UI-host direct intent dispatch helpers.
- Updated intent dispatch allowlist in `data/registries/intent_dispatch_whitelist.json`:
  - prepared `src/control/**` for CTRL-1 migration,
  - retained net ingress and test harness whitelists.

## Topology and Semantic Impact Integration
- Topology planning updated for upcoming control subsystem nodes:
  - `module:src/control`
  - `module:src/control/control_plane_engine.py`
  - `module:src/control/control_ir_validator.py`
  - `module:src/control/control_decision_log.py`
- Semantic impact routing updated so `src/control/**` changes require:
  - MP determinism suite,
  - RS-5 arbitration suite,
  - replay/reenactment suite.

## CTRL-1 Implementation Plan (Next)
1. Introduce `src/control/control_plane_engine.*` as the only authoritative dispatch gateway.
2. Implement control intent schema + deterministic parser and validator.
3. Implement control policy resolver (law/authority/server/profile aware) with deterministic downgrades.
4. Migrate interaction/tool/admin entrypoints to produce `ControlIntent` only.
5. Route execution through commitments/processes only; block residual direct dispatch paths.
6. Add proof-log artifact emission for all control decisions and downgrades.
7. Add replay session gating in control plane (derived-only controls).
8. Remove or quarantine migrated legacy dispatch paths once equivalence tests pass.

## Gate Notes
- RepoX (`python tools/xstack/repox/check.py --repo-root . --profile STRICT`):
  - PASS (`repox scan passed`, warn-only finding remains).
- AuditX (`python tools/xstack/auditx/check.py --repo-root . --profile STRICT`):
  - run complete / PASS status with warning findings.
- TestX doc/schema subset (`python tools/xstack/testx/runner.py --repo-root . --profile FAST --subset ...`):
  - PASS for:
    - `test_no_direct_intent_dispatch`
    - `test_topology_map_deterministic`
    - `test_topology_map_includes_all_schemas`
    - `test_topology_map_includes_all_registries`
    - `test_semantic_impact_outputs_stable`
    - `test_deprecation_registry_consistency`
- strict build (`py -3 tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.ctrl0 --cache on --format json`):
  - PASS (`result: complete`).

## Contract/Invariant Notes
- Canon/constitution alignment: unchanged.
- Ontology primitives: unchanged (no new ontology primitive introduced).
- Runtime semantics: unchanged; CTRL-0 is constitutional/documentation/enforcement preparation only.
- Determinism contract: preserved.
