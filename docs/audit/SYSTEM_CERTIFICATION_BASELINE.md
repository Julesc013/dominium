Status: BASELINE
Last Reviewed: 2026-03-06
Version: 1.0.0
Scope: SYS-5 System Certification & Compliance Workflow
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# System Certification Baseline

## Summary
SYS-5 establishes deterministic system certification workflows across system micro/macro tiers without hardcoding institution behavior.

Delivered capabilities:
- deterministic `process.system_evaluate_certification` evaluation over interface, invariants, SPEC compliance, safety patterns, and degradation state,
- canonical certification result rows and credential/report artifact emission,
- deterministic certificate revocation hooks on collapse/expand, degradation threshold breach, and SPEC violation,
- epistemic-aware inspection integration for certification and compliance sections,
- certification/revocation proof hash chains with replay-window verification tooling,
- RepoX/AuditX enforcement and dedicated SYS-5 TestX coverage.

## Certification Profiles
Registry:
- `data/registries/certification_profile_registry.json`

Declared profiles:
- `cert.basic_mechanical`
- `cert.pressure_vessel`
- `cert.electrical_installation`
- `cert.environmental_stub`

Profile rows declare:
- `required_spec_checks`
- `required_safety_patterns`
- `required_invariants`
- deterministic fingerprints and extension policy metadata.

## Issuance and Revocation Rules
Issuance path:
- process: `process.system_evaluate_certification`
- engine: `src/system/certification/system_cert_engine.py`
- outputs:
  - canonical `system_certification_result_rows`,
  - `artifact.record.system_certification_result`,
  - `artifact.report.system_certification_result`,
  - `artifact.credential.system_certificate` (pass-only).

Revocation path:
- canonical revocation through `_revoke_system_certifications(...)` in runtime.
- revocation triggers:
  - collapse (`event.system.certificate_revocation.collapse`)
  - expand (`event.system.certificate_revocation.expand`)
  - degradation threshold breach (`event.system.certificate_revocation.degradation_threshold`)
  - SPEC violation (`event.system.certificate_revocation.spec_violation`)
- revocation outputs:
  - `system_certificate_revocation_rows`,
  - `artifact.record.system_certificate_revocation`,
  - explain artifacts for revocation events.

## Explain Integration
Explain contracts:
- `explain.system.certification_failure`
- `explain.system.certificate_revocation`

Failure/revocation pathways now emit deterministic explain artifacts that are derived/compactable and anchored to certification hash chains.

## Proof and Replay Integration
State hash chains:
- `system_certification_result_hash_chain`
- `system_certificate_artifact_hash_chain`
- `system_certificate_revocation_hash_chain`

Alias compatibility keys:
- `certification_result_hash_chain`
- `certificate_artifact_hash_chain`
- `revocation_hash_chain`

Replay tool:
- `tools/system/tool_replay_certification_window.py`
- wrappers:
  - `tools/system/tool_replay_certification_window`
  - `tools/system/tool_replay_certification_window.cmd`

## Readiness for SYS-6
SYS-5 outputs are now suitable for SYS-6 reliability budgeting integration:
- deterministic credential lifecycle is tied to material system modification events,
- certification state and revocation chains are replay-verifiable and shard-safe,
- enforcement prevents direct SPEC bypass and silent certificate issuance paths.
