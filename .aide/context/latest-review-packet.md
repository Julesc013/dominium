# AIDE Review Packet

## Review Objective

Review `LANGUAGE-BASELINE-01`: active C17/C++17 mainline baseline, public ABI
preservation, macOS 10.9.5 C++17 subset policy, validators, build updates,
documentation, and evidence.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Evidence Packet References

- `contracts/build/language_baseline.contract.toml`
- `contracts/build/language_subset.schema.json`
- `tools/validators/build/check_language_baseline.py`
- `tools/validators/build/check_cpp17_forbidden_library_use.py`
- `docs/development/LANGUAGE_BASELINE.md`
- `docs/development/C17_USAGE_POLICY.md`
- `docs/development/CPP17_USAGE_POLICY.md`
- `docs/development/MACOS_10_9_CPP17_LIBRARY_SUBSET.md`
- `docs/architecture/C_COMPATIBLE_ABI_BOUNDARY.md`
- `.aide/reports/LANGUAGE-BASELINE-01-status.md`
- `.aide/reports/LANGUAGE-BASELINE-01-validation.md`
- `.aide/reports/LANGUAGE-BASELINE-01-results.json`
- `.aide/reports/LANGUAGE-BASELINE-01-language-inventory.md`
- `.aide/reports/LANGUAGE-BASELINE-01-fast-strict.json`
- `.aide/reports/LANGUAGE-BASELINE-01-fast-strict.md`
- `docs/repo/audits/LANGUAGE_BASELINE_01.md`

## Changed Files Summary

Moves active build and governance language surfaces to C17/C++17, preserves the
C-compatible public ABI law, adds macOS 10.9.5 restricted C++17 subset
validation, and records legacy projection warnings.

## Validation Summary

Fast strict passes with 32/32 commands in 318.25 seconds. Language baseline
validator passes with 7 legacy projection warnings. C++17 restricted library
validator passes with 1,192 files checked and 0 findings.

## Risk Summary

Full CTest remains T4/full-gate debt. Existing ABI warning debt remains
provisional and blocks stable/frozen ABI promotion. Legacy projection presets are
not active mainline.

## Non-Goals / Scope Guard

No feature implementation, release, tag, upload, renderer/native GUI behavior,
package runtime change, provider model, dependency direction law, compatibility
corpus, or full CTest proof.

## Reviewer Instructions

Confirm that active mainline has moved to C17/C++17 without leaking C++ ABI,
weakening the fast strict gate, or hiding legacy/full-gate debt.
