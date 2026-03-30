Status: DERIVED
Last Reviewed: 2026-03-30
Stability: stable
Future Series: XI-7
Replacement Target: superseded by a later explicit Xi-7 profile revision only

# CI Guardrails

Xi-7 makes CI the authoritative immune system against human and AI structural drift.

## Local Run

- POSIX: `tools/xstack/ci/xstack_ci_entrypoint --profile FAST`
- PowerShell: `tools/xstack/ci/xstack_ci_entrypoint.ps1 --profile FAST`
- Direct Python: `python -B tools/xstack/ci/xstack_ci_entrypoint.py --profile FAST`

## Deterministic Order

Every Xi-7 profile runs in this order:

1. `RepoX`
2. `AuditX`
3. `TestX`
4. `Validation + Omega`

The order is fixed in the committed Xi-7 profile artifacts under `tools/xstack/ci/profiles/`.

## Enforced RepoX Invariants

- `INV-NO-SRC-DIRECTORY`
- `INV-ARCH-GRAPH-V1-PRESENT`
- `INV-MODULE-BOUNDARIES-RESPECTED`
- `INV-SINGLE-CANONICAL-ENGINES`
- `INV-XSTACK-CI-MUST-RUN`
- `INV-STRICT-MUST-PASS-FOR-MAIN`

## Enforced AuditX Detectors

- `E560_ARCHITECTURE_DRIFT_SMELL`
- `E561_FORBIDDEN_DEPENDENCY_SMELL`
- `E562_DUPLICATE_SEMANTIC_ENGINE_REGISTRY_SMELL`
- `E563_UI_TRUTH_LEAK_BOUNDARY_SMELL`
- `AUDITX_NUMERIC_DISCIPLINE_SCAN`
- `E564_MISSING_CI_GUARD_SMELL`

## Profiles

- `FAST`: RepoX FAST, AuditX key drift/boundary checks, TestX FAST, `Ω-1`, `Ω-2`
- `STRICT`: RepoX STRICT, AuditX STRICT, TestX STRICT, `validate --all STRICT`, `ARCH-AUDIT-2`, `Ω-1..Ω-6`
- `FULL`: RepoX FULL, AuditX FULL, TestX FULL, STRICT validation plus convergence, performance, store, and optional archive verification

## Outputs

- `data/audit/ci_run_report.json`
- `docs/audit/CI_RUN_REPORT.md`

## Operating Rule

- prompts are untrusted
- CI is authoritative
- merge readiness must be supported by deterministic Xi-7 evidence, not prompt optimism
