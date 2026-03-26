Status: DERIVED
Last Reviewed: 2026-03-27
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI-5
Replacement Target: XI-5 bounded src-removal execution against approved mapping lock

# XI-5A Preflight Repair

## Scope

This pass repaired only the pre-existing validation blocker that prevented XI-5a from starting:

- `missing_stability` on `data/registries/toolchain_test_profile_registry.json`
- propagated as `refusal.validation.arch_audit` in FAST and STRICT aggregate validation

No src-domain mapping lock, approved layout, or repository structure decision was changed.

## Repairs Applied

1. Added entry-level `stability` markers to every `record.profiles[]` row in `data/registries/toolchain_test_profile_registry.json`.
2. Updated `tools/mvp/toolchain_matrix_common.py` so the canonical Ω-9 profile registry surface preserves and emits that same stability metadata.

The stability classification used is conservative and non-semantic:

- `stability_class_id`: `provisional`
- `future_series`: `TOOLCHAIN`
- `replacement_target`: `toolchain matrix and CI profile consolidation`

## Files Changed

- `data/registries/toolchain_test_profile_registry.json`
- `tools/mvp/toolchain_matrix_common.py`
- `data/audit/validation_report_FAST.json`
- `data/audit/validation_report_STRICT.json`
- `docs/audit/VALIDATION_REPORT_FAST.md`
- `docs/audit/VALIDATION_REPORT_STRICT.md`
- `docs/audit/VALIDATION_UNIFY_FINAL.md`

## Validation Before

- `validate --all FAST`: `refused`
- `validate --all STRICT`: `refused`
- blocking path: `data/registries/toolchain_test_profile_registry.json`
- blocking codes:
  - `missing_stability`
  - `refusal.validation.arch_audit`

## Validation After

- `validate --all FAST`: `complete`
- `validate --all STRICT`: `complete`
- errors after repair: `0`

## Execution Notes

- Final aggregate validation was rerun sequentially.
- TIME-ANCHOR validation uses deterministic scratch save roots under `saves/`, so concurrent aggregate validation runs are not a valid XI-5a preflight mode.

## XI-5A Readiness

XI-5a can now proceed unchanged against:

- `data/restructure/src_domain_mapping_lock_approved.json`
- `data/restructure/xi5_readiness_contract.json`

The preflight blocker was metadata and validation-surface alignment only. No runtime semantics changed.
