Status: DERIVED
Last Reviewed: 2026-05-21
Task: FOUNDATION-CLOSEOUT-02

# FOUNDATION-CLOSEOUT-02 Validation

Overall result: PASS_WITH_WARNINGS.

## Results

- dependency-direction strict: PASS, `16598` files scanned, `0` violations, `68` warnings.
- layer presence: PASS.
- Foundation validator matrix: PASS.
- AIDE doctor/validate/test/selftest/tools/roots/repo: PASS.
- RepoX STRICT: PASS with `INV-AUDITX-OUTPUT-STALE`.
- fast strict: PASS, `32` commands, `272.607` seconds.
- CMake configure/build: PASS through fast strict.
- smoke CTest: PASS through fast strict.
- generated-output policy: PASS.
- full CTest: NOT RUN; remains T4/full-gate debt.

## Evidence

- `.aide/reports/FOUNDATION-CLOSEOUT-02-dependency-direction.json`
- `.aide/reports/FOUNDATION-CLOSEOUT-02-layer-presence.json`
- `.aide/reports/FOUNDATION-CLOSEOUT-02-foundation-validator-matrix.json`
- `.aide/reports/FOUNDATION-CLOSEOUT-02-aide-validation.json`
- `.aide/reports/FOUNDATION-CLOSEOUT-02-repox-strict.md`
- `.aide/reports/FOUNDATION-CLOSEOUT-02-fast-strict.json`
- `.aide/reports/FOUNDATION-CLOSEOUT-02-generated-output.md`
