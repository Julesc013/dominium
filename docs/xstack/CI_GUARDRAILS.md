Status: DERIVED
Last Reviewed: 2026-03-30
Stability: stable
Future Series: XI-8
Replacement Target: superseded only by a later explicit CI guard profile revision

# CI Guardrails

Xi-8 extends the Xi-7 CI immune system with repository-structure freeze enforcement.

Local commands:

- `tools/xstack/ci/xstack_ci_entrypoint --profile FAST`
- `python -B tools/xstack/ci/xstack_ci_entrypoint.py --repo-root . --profile FAST`

## RepoX Rules

- `INV-NO-SRC-DIRECTORY`: Block reintroduction of generic src roots.
- `INV-ARCH-GRAPH-V1-PRESENT`: Require the Xi-6 frozen architecture graph and drift guard.
- `INV-REPO-STRUCTURE-LOCKED`: Require the Xi-8 repository structure lock and sanctioned source-pocket exceptions.
- `INV-ARCH-GRAPH-MATCHES-REPO`: Require live repository roots to stay registered in the Xi-6/Xi-8 frozen architecture surfaces.
- `INV-MODULE-BOUNDARIES-RESPECTED`: Block forbidden module dependencies.
- `INV-SINGLE-CANONICAL-ENGINES`: Block duplicate semantic engine implementations.
- `INV-XSTACK-CI-MUST-RUN`: Require the Xi-7/Xi-8 CI guardrail surface and workflow wiring.
- `INV-STRICT-MUST-PASS-FOR-MAIN`: Require the STRICT profile as the declared merge guard for main.

## AuditX Detectors

- `E560_ARCHITECTURE_DRIFT_SMELL`: Detect live module graph drift from the Xi-6 frozen architecture graph without an explicit update tag.
- `E561_FORBIDDEN_DEPENDENCY_SMELL`: Detect module boundary violations against module_boundary_rules.v1.
- `E562_DUPLICATE_SEMANTIC_ENGINE_REGISTRY_SMELL`: Detect duplicate semantic engines against the Xi-6 single-engine registry.
- `E563_UI_TRUTH_LEAK_BOUNDARY_SMELL`: Reinforce the constitutional renderer and UI truth-leak boundary.
- `E564_MISSING_CI_GUARD_SMELL`: Detect missing or incomplete Xi-7/Xi-8 CI guardrail surfaces and workflow wiring.
- `E565_REPOSITORY_STRUCTURE_DRIFT_SMELL`: Detect Xi-8 repository-structure drift, unsanctioned source pockets, and unknown top-level roots.
- `AUDITX_NUMERIC_DISCIPLINE_SCAN`: Run the deterministic numeric discipline scan as part of the Xi-8 audit surface.

## Profiles

- `FAST`: Default PR profile with Xi-8 structure lock enforcement, key AuditX scans, TestX FAST selection, and Ω-1/Ω-2 verification.
- `STRICT`: Required pre-merge profile with Xi-8 structure lock enforcement, strict validation, ARCH-AUDIT-2, Ω-1..Ω-6, and full RepoX/AuditX/TestX strict coverage.
- `FULL`: Nightly or pre-release profile with Xi-8 structure lock enforcement plus convergence, performance, store, and archive verification.

Prompts are untrusted.
CI is authoritative.
