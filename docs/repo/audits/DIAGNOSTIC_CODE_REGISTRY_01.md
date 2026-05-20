Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# DIAGNOSTIC-CODE-REGISTRY-01 Audit

## Status

PASS_WITH_WARNINGS.

## Why

Dominium needs stable, machine-readable diagnostics and evidence packets across
CLI, TUI, Workbench, headless tools, AIDE/Codex, tests, setup, package
validation, release proof, support/debugging, and runtime/service surfaces.
Free-text-only failures are not enough for portable recovery and proof.

## Added

- `contracts/diagnostics/diagnostic_code.registry.json`
- `contracts/diagnostics/diagnostic_code.schema.json`
- `contracts/diagnostics/diagnostic_severity.registry.json`
- `contracts/diagnostics/diagnostic_category.registry.json`
- `contracts/diagnostics/diagnostic_policy.contract.toml`
- `contracts/evidence/evidence_ref.schema.json`
- updated `contracts/evidence/evidence_packet.schema.json`
- updated `contracts/event/event.schema.json`
- updated `contracts/refusal/refusal_code.registry.json`
- `tools/validators/contracts/check_diagnostics_registry.py`
- `tests/contract/diagnostics/**`
- `docs/architecture/diagnostics_and_evidence.md`
- `docs/development/diagnostic_code_guidelines.md`

## Initial Registry

Registered 14 provisional diagnostic codes:

- `DOM-REPO-LAYOUT-VIOLATION`
- `DOM-REPO-FORBIDDEN-ROOT`
- `DOM-REPO-DEPENDENCY-DIRECTION-VIOLATION`
- `DOM-ABI-PUBLIC-HEADER-VIOLATION`
- `DOM-PUBLIC-SURFACE-INVALID`
- `DOM-CMD-INVALID-INPUT`
- `DOM-CMD-UNSUPPORTED-SURFACE`
- `DOM-CAPABILITY-MISSING`
- `DOM-PACK-INVALID-MANIFEST`
- `DOM-SCHEMA-UNSUPPORTED-VERSION`
- `DOM-EVIDENCE-MISSING`
- `DOM-FULL-GATE-DEBT`
- `DOM-AIDE-TASK-BLOCKED`
- `DOM-RELEASE-PROMOTION-BLOCKED`

No diagnostic is marked stable. No runtime diagnostic dispatcher, Workbench UI,
product behavior, package runtime, gameplay, renderer, native GUI behavior, or
release publication was implemented.

## Proof

- Diagnostic validator strict: PASS, 14 codes, 7 severities, 26 categories, 0 findings.
- Diagnostic validator fixtures: PASS.
- Public surface validator: PASS, 47 surfaces.
- Command surface validator: PASS.
- ABI validator: PASS with 2,851 existing warnings.
- Dependency direction validator: FAIL on known existing debt from
  DEPENDENCY-DIRECTION-01; latest scan checked 16,153 files with
  358 violations and 38 warnings.
- Fast strict: PASS, 32/32 commands, 351.282 seconds.
- Remaining validation details are recorded in
  `.aide/reports/DIAGNOSTIC-CODE-REGISTRY-01-validation.md`.

## Known Warnings

- Diagnostic registry law is provisional.
- Runtime diagnostic dispatch remains future work.
- Workbench presentation remains future work.
- Capability/refusal and artifact identity laws remain later Foundation Lock work.
- Dependency-direction strict debt remains visible and unresolved.
- Full CTest was not run and remains T4 full/release proof.

## Next Task

`ARTIFACT-IDENTITY-LAW-01`.
