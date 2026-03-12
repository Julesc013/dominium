Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# System Composition Baseline

Status: BASELINE (SYS-0)  
Date: 2026-03-05  
Scope: System composition constitution, collapse/expand process skeletons, boundary invariant declarations, and SYS-0 enforcement/test coverage.

## 1) System Definition Summary

SYS-0 defines a System as a rooted connected assembly subgraph with explicit contracts:

- interface signature (ports, bundles, signals, limits)
- tier contract (micro/meso/macro progression)
- coupling contracts
- safety contracts

Core constitution and audit surfaces:

- `docs/system/SYSTEM_COMPOSITION_CONSTITUTION.md`
- `docs/audit/SYS0_RETRO_AUDIT.md`

## 2) Collapse / Expand Rules

Authoritative operations are process-only:

- `process.system_collapse`
- `process.system_expand`

Implemented skeleton behavior:

- collapse validates eligibility and boundary invariants
- collapse captures deterministic internal state vector + provenance anchor hash
- collapse creates macro capsule artifact and replaces internal graph with capsule placeholder
- expand restores internal graph from serialized state
- expand validates provenance anchor and refuses on mismatch

Primary runtime surfaces:

- `src/system/system_collapse_engine.py`
- `src/system/system_expand_engine.py`
- `tools/xstack/sessionx/process_runtime.py`

## 3) Boundary Invariants

Declared invariant baseline:

- `invariant.mass_conserved`
- `invariant.energy_conserved`
- `invariant.momentum_conserved`
- `invariant.pollutant_accounted`

Registry/schema anchors:

- `data/registries/system_boundary_invariant_registry.json`
- `schema/system/interface_signature.schema`
- `schema/system/boundary_invariant.schema`
- `schema/system/macro_capsule.schema`
- `schema/system/system_state_vector.schema`

## 4) Enforcement and Test Coverage

RepoX invariants added for SYS-0:

- `INV-NO-HIDDEN-SYSTEM-STATE`
- `INV-SYSTEM-BOUNDARY-INVARIANTS-DECLARED`
- `INV-COLLAPSE-ONLY-VIA-PROCESS`

AuditX analyzers added:

- `E258_IMPLICIT_SYSTEM_COLLAPSE_SMELL` (`ImplicitSystemCollapseSmell`)
- `E259_HIDDEN_SYSTEM_STATE_SMELL` (`HiddenStateSmell`)

TestX coverage added:

- `test_system_collapse_expand_roundtrip`
- `test_boundary_invariant_preserved_after_collapse`
- `test_no_hidden_state_influence`
- `test_provenance_anchor_validation`
- `test_cross_platform_capsule_hash_match`

## 5) Gate Execution

Validation level executed: STRICT governance gates plus explicit SYS-0 TestX subset.

- topology map updated:
  - command: `py -3 tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
  - result: `complete`
  - deterministic_fingerprint: `9db47748a1ca9823c6eb42ca7e2f27b956916063678e6009043abc3ce04f2aa0`
- RepoX STRICT:
  - command: `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - result: `pass` (`findings=17`, warnings only)
- AuditX STRICT:
  - command: `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - result: `pass` (`findings=1313`, `promoted_blockers=0`)
- TestX PASS (SYS-0 required subset):
  - command: `py -3 tools/xstack/testx/runner.py --profile STRICT --cache off --subset test_system_collapse_expand_roundtrip,test_boundary_invariant_preserved_after_collapse,test_no_hidden_state_influence,test_provenance_anchor_validation,test_cross_platform_capsule_hash_match`
  - result: `pass` (`selected_tests=5`)
- strict build:
  - command: `py -3 tools/xstack/run.py strict --repo-root . --cache on`
  - result: `refusal` (global baseline blockers outside SYS-0 scope)
  - blocking steps:
    - `01.compatx.check` refusal
    - `04.registry.compile` refusal
    - `07.session_boot.smoke` refusal
    - `10.testx.run` fail (global strict suite)
    - `13.packaging.verify` refusal

## 6) Readiness

SYS-0 baseline is ready for:

- SYS-1 interface signature and invariant enforcement hardening
- SYS-2 macro model binding and active capsule behavior

No domain semantics were changed; SYS-0 introduces composition/collapse scaffolding only.
