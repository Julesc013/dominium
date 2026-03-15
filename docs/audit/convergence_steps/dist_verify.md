Status: DERIVED
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: RELEASE
Replacement Target: regenerated convergence step summary for dist_verify

# Convergence Step - DIST-2 distribution integrity verification

- step_no: `1`
- step_id: `dist_verify`
- result: `complete`
- rule_id: `INV-DIST-VERIFY-MUST-PASS`
- source_fingerprint: `c4976ffdda1526f9450334d912fdbe578291c64776d34ec58bf6bffff433d5d9`
- observed_refusal_count: `0`
- observed_degrade_count: `0`

## Key Hashes

- dist_verify_fingerprint: `c4976ffdda1526f9450334d912fdbe578291c64776d34ec58bf6bffff433d5d9`
- filelist_hash: `d4f206b381d2314ae9e931cd20c16ed1c19bd3f764753768878b4f2f9e98e5c3`
- release_manifest_hash: `1630c519b6c04299f8eeefb4ea58a9e0af883550dfcb0d226f77fe6b3dfb7fdc`

## Notes

- platform_tag=win64
- bundle_root=dist/v0.0.0-mock/win64/dominium

## Source Paths

- `data/audit/dist_verify_win64.json`
- `docs/audit/DIST_VERIFY_win64.md`

## Remediation

- module=`tools/dist/tool_verify_distribution.py` rule=`INV-DIST-VERIFY-MUST-PASS` refusal=`none` command=`python tools/dist/tool_verify_distribution.py --repo-root . --platform-tag win64`
