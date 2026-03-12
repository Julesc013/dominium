Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# System Interface & Invariant Baseline

Status: BASELINE (SYS-1)  
Date: 2026-03-05  
Scope: interface signature completeness enforcement, boundary invariant validation, spec/safety integration, macro model set compatibility checks, and SYS-1 enforcement/test coverage.

## 1) Interface Templates

Interface signature template registry added:

- `interface.engine_basic`
- `interface.generator_basic`
- `interface.pump_basic`
- `interface.heat_exchanger_basic`
- `interface.vehicle_propulsion_basic`

Registry anchor:

- `data/registries/interface_signature_template_registry.json`

## 2) Boundary Invariant Templates

Boundary invariant template registry added:

- `inv.mass_energy_basic`
- `inv.energy_pollution_basic`
- `inv.momentum_basic`
- `inv.safety_failsafe_required`

Registry anchors:

- `data/registries/boundary_invariant_template_registry.json`
- `data/registries/macro_model_set_registry.json` (stub/empty for SYS-2 population)

## 3) Validation Behavior

Deterministic validation engine implemented:

- `validate_interface_signature(system_id)` enforces boundary port descriptors, bundle registration, signal descriptors, and spec limit references.
- `validate_boundary_invariants(system_id)` enforces invariant templates, tolerance policy presence, energy-ledger requirement for energy invariants, pollution accounting rules, and required safety pattern coverage.
- `validate_macro_model_set(capsule_id)` enforces macro model registration, signature compatibility with interface bundles/signals, and error-bound policy presence.

Primary runtime surface:

- `src/system/system_validation_engine.py`

## 4) Collapse/Expand Integration

SYS-0 process skeletons were upgraded so validation is mandatory on transition:

- `process.system_collapse` now validates interface signatures and boundary invariants before capsule creation.
- deterministic refusals emitted for invalid interface/invariant conditions:
  - `refusal.system.invalid_interface`
  - `refusal.system.invariant_violation`
- `process.system_expand` validates restored signature/invariants before rebind completion.

Integration surfaces:

- `src/system/system_collapse_engine.py`
- `src/system/system_expand_engine.py`
- `tools/xstack/sessionx/process_runtime.py`

## 5) Spec and Safety Integration

SYS-1 validation now executes spec and safety checks as part of interface/invariant enforcement:

- spec limit references must resolve to registered spec entries.
- invariant templates can require safety pattern IDs, and missing required patterns produce deterministic refusal findings.
- this enforces certification prerequisites ahead of SYS-5 without introducing silent bypass.

Authoritative doctrine:

- `docs/system/INTERFACE_AND_INVARIANT_RULES.md`

## 6) Enforcement and Test Coverage

RepoX invariants added:

- `INV-SYSTEM-INTERFACE-SIGNATURE-REQUIRED`
- `INV-SYSTEM-INVARIANTS-REQUIRED`
- `INV-MACRO-MODEL-SET-REQUIRED-FOR-CAPSULE`

AuditX analyzers added:

- `E260_MISSING_INTERFACE_DESCRIPTOR_SMELL` (`MissingInterfaceDescriptorSmell`)
- `E261_MISSING_INVARIANT_TEMPLATE_SMELL` (`MissingInvariantTemplateSmell`)
- `E262_MACRO_MODEL_SIGNATURE_MISMATCH_SMELL` (`MacroModelSignatureMismatchSmell`)

TestX coverage added:

- `test_interface_signature_validation`
- `test_invariant_validation_energy_requires_ledger`
- `test_spec_limit_validation`
- `test_collapse_refused_on_invalid_interface`
- `test_macro_model_set_signature_match`
- `test_cross_platform_validation_hash`

## 7) Gate Execution

Validation level executed: STRICT governance gates + SYS-1 target TestX subset.

- topology map updated:
  - command: `py -3 tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
  - result: `complete`
  - deterministic_fingerprint: `013be8b5a7546eb6054af43967dbfd4231640e4448cf9d438767351c55799cc9`

- RepoX STRICT:
  - command: `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - result in pre-commit run: `refusal`
  - refusal cause: `INV-WORKTREE-HYGIENE` while SYS-1 and topology artifacts were pending commit

- AuditX STRICT:
  - command: `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - result: `pass` (`findings=1325`, `promoted_blockers=0`)

- TestX PASS (SYS-1 required subset):
  - command: `py -3 tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset test_interface_signature_validation,test_invariant_validation_energy_requires_ledger,test_spec_limit_validation,test_collapse_refused_on_invalid_interface,test_macro_model_set_signature_match,test_cross_platform_validation_hash`
  - result: `pass` (`selected_tests=6`)

- strict build:
  - command: `py -3 tools/xstack/run.py strict --repo-root . --cache on`
  - result: `refusal` due repository-global strict-lane blockers outside SYS-1 scope (`compatx`, `registry_compile`, `session_boot`, full-lane `testx`, `packaging.verify`)

## 8) Readiness

SYS-1 baseline is ready for:

- SYS-2 macro capsule behavior models and runtime binding execution
- SYS-3 tier/ROI transition orchestration over validated interfaces

No new solver introduced; domain semantics remain unchanged.
