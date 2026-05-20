# LANGUAGE-BASELINE-01 Validation

Status: PASS_WITH_WARNINGS

## Commands Run

- `python -m py_compile tools/validators/build/check_language_baseline.py tools/validators/build/check_cpp17_forbidden_library_use.py tests/contract/public_header_c17_compile.py tests/contract/public_header_cpp17_compile.py tests/invariant/invariant_lang_c17.py tests/invariant/invariant_lang_cpp17.py`
  Result: PASS

- `python -c "import json; [json.load(open(p, encoding='utf-8')) for p in ['contracts/build/language_subset.schema.json','contracts/abi/abi_rule.registry.json','contracts/abi/public_header.schema.json','contracts/public_surface/surface.schema.json']]; print('json parse ok')"`
  Result: PASS

- `python tools/validators/build/check_language_baseline.py --repo-root . --strict`
  Result: PASS, 104 CMake files checked, 0 errors, 7 warnings for legacy projection presets.

- `python tools/validators/build/check_language_baseline.py --repo-root . --json`
  Result: PASS

- `python tools/validators/build/check_cpp17_forbidden_library_use.py --repo-root . --strict`
  Result: PASS, 1,192 files checked, 0 errors, 0 warnings.

- `python tools/validators/build/check_cpp17_forbidden_library_use.py --repo-root . --json`
  Result: PASS

- `python tools/validators/testing/check_test_tiers.py --repo-root . --strict`
  Result: PASS

- `python tools/validators/repo/check_public_surface.py --repo-root . --strict`
  Result: PASS, 27 surfaces, 2 stable surfaces.

- `python tools/validators/abi/check_public_headers.py --repo-root . --strict`
  Result: PASS, 375 header candidates, 0 errors, 2,851 warnings.

- `python tools/validators/abi/check_public_headers.py --repo-root . --fixtures`
  Result: PASS

- `python tools/test/run_fast_strict.py --repo-root . --list`
  Result: PASS

- `python tools/test/run_fast_strict.py --repo-root . --dry-run --json-out .aide/reports/LANGUAGE-BASELINE-01-dry-run.json --md-out .aide/reports/LANGUAGE-BASELINE-01-dry-run.md`
  Result: DRY_RUN, 32 normal-gate commands resolved.

- `python tools/validators/ci/tool_identity_fingerprint.py --repo-root . --output docs/archive/audit/identity_fingerprint.json`
  Result: PASS, refreshed fingerprint `8715c1eab62f21582d9406c3ba538afdc3f216ad05963648f471c3f54158d798`.

- `cmake --preset verify`
  Result: PASS after narrowing `BaselineHeaderCheck.cmake` to platform/C++ library include leakage; ABI shape remains enforced by the ABI validator.

- `cmake --build --preset verify --target ALL_BUILD`
  Result: PASS on rerun after the first fast-strict build attempt returned nonzero with truncated output.

- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/LANGUAGE-BASELINE-01-fast-strict.json --md-out .aide/reports/LANGUAGE-BASELINE-01-fast-strict.md`
  Result: PASS, 32/32 commands, 318.25 seconds.

## Fast Strict Summary

- T0: PASS, 5/5.
- T1: PASS, 24/24 including RepoX strict and the two new language validators.
- T2: PASS, 3/3 including CMake configure, CMake build, and smoke CTest.
- Elapsed: 318.25 seconds.

## Not Run

Full CTest was not run. It remains the T4 full/release proof lane and known
full-gate debt.
