# LANGUAGE-BASELINE-01 Status

Status: PASS_WITH_WARNINGS

Branch: `main`

Starting HEAD: `502daf57d4fda8bf2916677cd6fc322ce688d030`

Origin/main at start: `502daf57d4fda8bf2916677cd6fc322ce688d030`

## Summary

Dominium mainline is now governed as C17 + C++17 across active source, build,
validation, and documentation surfaces.

- Active CMake root and target standards moved from C90/C++98 to C17/C++17.
- `CMakePresets.json` active verify/dev/release presets now use C17/C++17.
- Public ABI doctrine remains C-compatible and does not expose C++ ABI.
- C++17 usage is restricted for macOS 10.9.5 deployment compatibility.
- Retro C89/C++98 lanes are historical or future research only.
- Feature work remains blocked until Foundation Lock closes.

## Key Files

- `contracts/build/language_baseline.contract.toml`
- `contracts/build/language_subset.schema.json`
- `tools/validators/build/check_language_baseline.py`
- `tools/validators/build/check_cpp17_forbidden_library_use.py`
- `docs/development/LANGUAGE_BASELINE.md`
- `docs/development/C17_USAGE_POLICY.md`
- `docs/development/CPP17_USAGE_POLICY.md`
- `docs/development/MACOS_10_9_CPP17_LIBRARY_SUBSET.md`
- `docs/architecture/C_COMPATIBLE_ABI_BOUNDARY.md`
- `.aide/reports/LANGUAGE-BASELINE-01-fast-strict.json`
- `.aide/reports/LANGUAGE-BASELINE-01-fast-strict.md`

## Result

- Language baseline validator: PASS with 7 legacy projection warnings.
- C++17 restricted library validator: PASS with 0 findings.
- Public surface validator: PASS, 27 surfaces.
- Public header ABI validator: PASS, 375 candidates, 0 errors, 2,851 warnings.
- Fast strict gate: PASS, 32/32 commands, 318.25 seconds.
- Full CTest: not run; remains T4 full/release proof and known debt.

## Warnings

Seven advanced IDE projection presets still declare `DOM_LANG_MODE=c89_cpp98`.
They are legacy/projection lanes outside active mainline and are warning-only.

Full CTest remains separate T4/full-gate debt and is not claimed green.

Next task: `DEPENDENCY-DIRECTION-01`.
