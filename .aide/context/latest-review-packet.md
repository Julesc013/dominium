# AIDE Review Packet

## Review Objective

Review `API-ABI-CANON-01`: provisional C API/ABI canon, public-header validator,
fixtures, documentation, public-surface registry updates, and evidence.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/verification/latest-verification-report.md`

## Evidence Packet References

- `contracts/abi/c_api.contract.toml`
- `contracts/abi/language_boundary.contract.toml`
- `contracts/abi/abi_rule.registry.json`
- `contracts/abi/public_header.schema.json`
- `tools/validators/abi/check_public_headers.py`
- `tests/contract/public_headers/**`
- `docs/architecture/api_abi_canon.md`
- `docs/development/c89_coding_standard.md`
- `docs/development/cpp98_implementation_standard.md`
- `docs/development/module_api_standard.md`
- `contracts/public_surface/public_surface.contract.toml`
- `.aide/reports/API-ABI-CANON-01-status.md`
- `.aide/reports/API-ABI-CANON-01-validation.md`
- `.aide/reports/API-ABI-CANON-01-results.json`
- `.aide/reports/API-ABI-CANON-01-public-header-inventory.md`
- `docs/repo/audits/API_ABI_CANON_01.md`

## Changed Files Summary

Adds provisional C89/C++98 API/ABI law, a stdlib public-header validator,
fixture headers, docs, AIDE evidence, and conservative public-surface registry
entries. Existing headers are not renamed or behaviorally changed.

## Validation Summary

ABI validator passes with 375 candidates, 0 high-confidence violations, and
2,851 warnings. The warnings are retained as stable/frozen ABI promotion
blockers. Public surface validator passes with 25 registered surfaces.

## Risk Summary

No public ABI is frozen. Existing `dom_`/`d_` prefixes, ABI-like struct shape,
C++ declarations, and callback context gaps remain visible provisional debt.
Compatibility corpus and deeper consumer compile proof remain later work.

## Token Summary

The packet stays compact and references evidence by path.

## Non-Goals / Scope Guard

No feature implementation, release, tag, upload, renderer/native GUI behavior,
package runtime change, provider model, dependency direction law, compatibility
corpus, or full CTest proof.

## Reviewer Instructions

Confirm that the task defines and validates ABI law without freezing unproven
headers, weakening existing validators, or hiding warning debt.
