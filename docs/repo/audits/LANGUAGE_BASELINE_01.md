# LANGUAGE_BASELINE_01

Status: PASS_WITH_WARNINGS

## Why

Dominium mainline now targets Windows 7 SP1, macOS 10.9.5, and Linux. The old
C90/C++98 active baseline imposed implementation cost without matching that
floor. This task moves active source and build governance to C17 + C++17 while
preserving a C-compatible public ABI and deterministic proof discipline.

## Changed

- Added `contracts/build/language_baseline.contract.toml`.
- Added `contracts/build/language_subset.schema.json`.
- Added `tools/validators/build/check_language_baseline.py`.
- Added `tools/validators/build/check_cpp17_forbidden_library_use.py`.
- Updated active CMake and preset language standards to C17/C++17.
- Updated ABI/public-surface/test-tier contracts to reference C17/C++17.
- Added C17/C++17 language usage docs and macOS 10.9 C++17 subset guidance.
- Refreshed `docs/archive/audit/identity_fingerprint.json` after canon index changes.

## Policy

- C17 is the mainline C floor.
- C++17 is the mainline C++ floor.
- Public ABI remains C-compatible.
- C++ ABI, STL types, exceptions, RTTI, and platform headers must not leak across stable public ABI.
- C17 atomics/threads/complex are not the portable cross-platform concurrency substrate.
- macOS 10.9.5 requires a restricted C++17 library subset.
- C89/C++98 is retired from active mainline and remains only historical or future retro/research lane material.

## Proof

- Language baseline validator: PASS with 7 legacy projection warnings.
- C++17 restricted library validator: PASS, 1,192 files checked, 0 findings.
- Public surface validator: PASS, 27 surfaces.
- Public header ABI validator: PASS, 375 candidates, 0 errors, 2,851 warnings.
- Fast strict gate: PASS, 32/32 commands, 318.25 seconds.
- Smoke CTest: PASS through fast strict.
- Full CTest: not run; remains T4 full/release proof.

## Known Warnings

Seven advanced IDE projection presets remain marked with `DOM_LANG_MODE=c89_cpp98`.
They are legacy/projection lanes outside the active mainline.

Public header ABI warnings remain provisional ABI debt and stable/frozen promotion
blockers. No public ABI was frozen by this task.

Next task: `DEPENDENCY-DIRECTION-01`.
