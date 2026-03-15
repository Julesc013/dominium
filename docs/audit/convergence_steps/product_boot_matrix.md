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
- source_fingerprint: `46287351a02e104f93329b48215832426e46d77c43892c10303126ad543e9201`
- observed_refusal_count: `0`
- observed_degrade_count: `10`

## Key Hashes

- product_boot_matrix_fingerprint: `46287351a02e104f93329b48215832426e46d77c43892c10303126ad543e9201`

## Notes

- portable_and_installed_matrix_exercised=true
- failure_count=0

## Source Paths

- `data/audit/product_boot_matrix.json`
- `docs/mvp/PRODUCT_BOOT_MATRIX.md`

## Remediation

- module=`tools/mvp/tool_run_product_boot_matrix.py` rule=`INV-PROD-GATE-0-MUST-PASS-BEFORE-RELEASE` refusal=`none` command=`python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
