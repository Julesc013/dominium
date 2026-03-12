Status: AUTHORITATIVE
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: RELEASE-GOV
Replacement Target: release-pinned validation governance constitution

# Validation Pipeline

This document defines the unified validation surface for `validate --all`.
It consolidates the repository validation stack into one deterministic, ordered pipeline without removing legacy validators during `v0.0.0`.

## Command Surface

- Governed products expose: `validate --all [--profile FAST|STRICT|FULL]`
- The command runs through AppShell.
- Validation ordering is registry-driven through [validation_suite_registry.json](/d:/Projects/Dominium/dominium/data/registries/validation_suite_registry.json).

## Categories

- `validate.schemas`: CompatX validation for the governed validation/contract/pack/time-anchor schemas exercised by the unified pipeline, using a deterministic scoped schema workspace.
- `validate.registries`: registry stability markers and governed registry structure validation.
- `validate.contracts`: semantic contract registry and default universe contract bundle validation.
- `validate.packs`: release pack-lock validation, rebuilt MVP runtime pack-lock comparison, and `pack.compat.json` governance checks for the PACK-COMPAT surface.
- `validate.negotiation`: CAP-NEG descriptor negotiation and negotiation-record verification.
- `validate.library`: LIB install registry verification plus release-surface install/instance/save/artifact manifest checks.
- `validate.time_anchor`: TIME-ANCHOR long-run tick and compaction-anchor verification.
- `validate.arch_audit`: ARCH-AUDIT constitutional structure scan.
- `validate.determinism`: deterministic static scans for wall-clock, unnamed RNG, unordered iteration, and unreviewed float usage.
- `validate.platform_matrix`: optional cached cross-platform agreement verification for `FULL`.

## Profiles

- `FAST`: run all core suites except optional platform matrix.
- `STRICT`: same ordered suites as `FAST`, with strict schema checks enabled through CompatX.
- `FULL`: includes `STRICT` plus optional platform-matrix coverage if the cached Gate 2 report is present.
- Profiles are intended to be executed serially; the current TIME-ANCHOR verifier uses deterministic fixed fixture paths and is not designed for concurrent profile execution.

## Structured Result

Each suite returns a normalized validation result shaped by:
- [validation_result.schema](/d:/Projects/Dominium/dominium/schema/validation/validation_result.schema)
- [validation_result.schema.json](/d:/Projects/Dominium/dominium/schemas/validation_result.schema.json)

Required result properties include:
- `suite_id`
- `category_id`
- `profile`
- `result`
- `errors`
- `warnings`
- `legacy_adapters`
- `deterministic_fingerprint`

## Legacy Validators

Legacy validators are not deleted during MVP convergence.
They are handled in one of two ways:

- `direct_python`: the unified engine calls the existing validator logic directly through an adapter.
- `coverage_adapter`: the legacy entrypoint is deprecated and mapped to the unified suite that now owns its responsibility.

Deprecated surfaces remain provisional and must keep explicit replacement targets.

## Outputs

For a given profile `<P>` the pipeline writes:

- [VALIDATION_REPORT_FAST.md](/d:/Projects/Dominium/dominium/docs/audit/VALIDATION_REPORT_FAST.md) or the matching profile variant
- [validation_report_FAST.json](/d:/Projects/Dominium/dominium/data/audit/validation_report_FAST.json) or the matching profile variant
- [VALIDATION_INVENTORY.md](/d:/Projects/Dominium/dominium/docs/audit/VALIDATION_INVENTORY.md)
- [VALIDATION_UNIFY_FINAL.md](/d:/Projects/Dominium/dominium/docs/audit/VALIDATION_UNIFY_FINAL.md)

## Invariants

- Suite order is deterministic and registry-declared.
- Validation does not mutate TruthModel.
- Legacy validation surfaces must map to a unified suite or be reported as drift.
- `validate --all` must remain AppShell-accessible for governed products.
