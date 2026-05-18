Status: PASS_WITH_WARNINGS
Last Reviewed: 2026-05-18
Task: MOVE-ROUTER-00

# MOVE-ROUTER-00 Blockers

No MOVE-ROUTER-00 dry-run blocker remains.

## Cleared

- Target collisions: 0.
- Skipped/impossible routes: 0.
- Every tracked bad-root file has a proposed target.
- Unknown or ambiguous files route to `archive/quarantine/<root>/`.

## Remaining Apply Risks

These are not blockers for MOVE-ROUTER-00 because no files were moved:

- 71 quarantine routes require later owner review before promotion.
- 227 import rewrite candidates require apply/repair handling.
- 121 shim candidates require explicit authorization if shims are needed.
- 3 target paths were sanitized to avoid forbidden directory names.
- Bad-root exceptions remain active until roots are empty after apply.

## Not Authorized

- No physical moves.
- No reference rewrites.
- No import rewrites.
- No temporary shims.
- No exception retirement.
- No feature work.
