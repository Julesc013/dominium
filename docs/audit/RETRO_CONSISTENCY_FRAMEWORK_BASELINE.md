Status: DERIVED
Last Reviewed: 2026-02-28
Version: 1.0.0
Scope: ARCH-REF-1 Retro-consistency framework baseline.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Retro Consistency Framework Baseline

## Doctrine Summary
- Added canonical framework document: `docs/architecture/RETRO_CONSISTENCY_AUDIT_FRAMEWORK.md`.
- Established mandatory `PHASE 0 — Retro-Consistency Audit` for future major subsystem prompts.
- Enforced replacement-over-addition and deterministic drift prevention rules.

## Duplication Detection Rules
- Added canonical rule specification: `docs/architecture/DUPLICATION_DETECTION_RULES.md`.
- Mechanical detection classes:
  - graph duplication
  - flow duplication
  - state duplication
  - schedule duplication
  - hazard duplication
  - direct intent dispatch bypass
  - legacy reference in production paths

## Deprecation Policy
- Added deprecation/quarantine policy: `docs/architecture/DEPRECATION_AND_QUARANTINE.md`.
- Added deprecation schema artifacts:
  - `schema/deprecation/deprecation_entry.schema`
  - `schemas/deprecation_entry.schema.json`
  - `schemas/deprecation_registry.schema.json`
  - `data/registries/deprecation_registry.json`

## Enforcement Rules
- RepoX strict/warn profile enforcement added:
  - `INV-NO-DUPLICATE-GRAPH`
  - `INV-NO-DUPLICATE-FLOW`
  - `INV-NO-ADHOC-STATE-FLAG`
  - `INV-NO-ADHOC-SCHEDULER`
  - `INV-NO-ADHOC-HAZARD`
  - `INV-NO-DIRECT-INTENT-DISPATCH`
  - `INV-NO-LEGACY-REFERENCE`
- FAST profile behavior: warnings.
- STRICT/FULL profile behavior: refusal/fail by invariant severity policy.

## Analyzer Coverage
- Existing analyzers cover:
  - `GraphDuplicationSmell` (`E84_GRAPH_DUPLICATION_SMELL`)
  - `FlowBypassSmell` (`E87_FLOW_BYPASS_SMELL`)
  - `StateFlagSmell` (`E93_ADHOC_STATE_FLAG_SMELL`)
  - `SchedulerDuplicationSmell` (`E94_DUPLICATE_SCHEDULER_SMELL`)
  - `HazardDuplicationSmell` (`E95_HAZARD_LOGIC_DUPLICATION_SMELL`)
- Added analyzers:
  - `DirectIntentBypassSmell` (`E104_DIRECT_INTENT_BYPASS_SMELL`)
  - `LegacyReferenceSmell` (`E105_LEGACY_REFERENCE_SMELL`)

## Migration Template
- Added mandatory migration template: `docs/architecture/MIGRATION_TEMPLATE.md`.
- Required sections:
  - overlap identification
  - replacement abstraction
  - migration steps
  - compatibility strategy
  - equivalence tests
  - RepoX additions
  - deprecation entry

## TestX Coverage
- Added tests:
  - `test_no_duplicate_graph_structs`
  - `test_no_duplicate_flow_logic`
  - `test_no_ad_hoc_state_flags`
  - `test_legacy_directory_not_linked`
  - `test_deprecation_registry_consistency`

## Gate Notes
- RepoX (`python tools/xstack/repox/check.py --repo-root . --profile STRICT`):
  - PASS
  - `repox scan passed (files=1037, findings=1)` (`INV-AUDITX-REPORT-STRUCTURE` warn only).
- AuditX (`python tools/xstack/auditx/check.py --repo-root . --profile STRICT`):
  - run complete / PASS status
  - `auditx scan complete (changed_only=false, findings=1694)` (warning findings reported).
- TestX ARCH1 subset (`python tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset ...`):
  - PASS for all added tests:
    - `test_no_duplicate_graph_structs`
    - `test_no_duplicate_flow_logic`
    - `test_no_ad_hoc_state_flags`
    - `test_legacy_directory_not_linked`
    - `test_deprecation_registry_consistency`
- strict profile run (`python tools/xstack/run.py strict --repo-root . --cache on`):
  - REFUSAL (`exit_code=2`)
  - blocking steps:
    - `01.compatx.check` refusal (`findings=161`, existing strict compat requirements)
    - `10.testx.run` fail (`selected_tests=386`, global suite findings outside ARCH1 subset)
    - `13.packaging.verify` refusal (`lab build validation refused`)
  - report: `tools/xstack/out/strict/latest/report.json`
- ui_bind (`python tools/xstack/ui_bind.py --repo-root . --check`):
  - PASS (`checked_windows=21`)
