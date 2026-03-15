Status: DERIVED
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: RELEASE
Replacement Target: regenerated convergence step summary for product_boot_matrix

# Convergence Step - PROD-GATE-0 boot matrix

- step_no: `8`
- step_id: `product_boot_matrix`
- result: `complete`
- rule_id: `INV-PROD-GATE-0-MUST-PASS-BEFORE-RELEASE`
- source_fingerprint: `b3e5e548cad7bfa7c6abe688f2cf6cc5c1571ff19812dfd5c5f1599f41f17d9f`
- observed_refusal_count: `0`
- observed_degrade_count: `10`

## Key Hashes

- product_boot_matrix_fingerprint: `b3e5e548cad7bfa7c6abe688f2cf6cc5c1571ff19812dfd5c5f1599f41f17d9f`

## Notes

- portable_and_installed_matrix_exercised=true
- failure_count=0

## Source Paths

- `data/audit/product_boot_matrix.json`
- `docs/mvp/PRODUCT_BOOT_MATRIX.md`

## Remediation

- module=`tools/mvp/tool_run_product_boot_matrix.py` rule=`INV-PROD-GATE-0-MUST-PASS-BEFORE-RELEASE` refusal=`none` command=`python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
