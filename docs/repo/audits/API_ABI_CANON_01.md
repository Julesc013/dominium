Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Stability: provisional
Binding Sources: `contracts/abi/c_api.contract.toml`, `contracts/abi/language_boundary.contract.toml`, `contracts/public_surface/public_surface.contract.toml`, `docs/architecture/api_abi_canon.md`

# API-ABI-CANON-01 Audit

## Status

PASS_WITH_WARNINGS.

## Why

Dominium needs enforceable API/ABI law before exposing stable public headers,
providers, modules, command surfaces, native shells, or long-lived artifacts.
This task defines the rules without freezing existing provisional headers.

## Added

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

## Registry Updates

The public surface registry now records ABI canon surfaces, the ABI rule
registry, the public-header schema, and public-header fixtures. Engine, runtime,
and game header umbrella surfaces remain provisional. No surface is promoted to
`frozen_abi`.

## Public Header Inventory

- Candidates inspected: 375
- High-confidence violations: 0
- Warnings: 2,851
- Main warning classes: legacy `dom_`/`d_` prefixes, unprefixed declarations,
  ABI-like structs without `struct_size`, non-frozen C++ declarations, and
  callback context gaps.

Warnings are stable-promotion blockers, not hidden passes.

## Proof

- ABI validator strict/json/fixtures: PASS
- Public surface validator: PASS
- Docs/include/build/UI/ABI supplemental validators: PASS
- RepoX STRICT: PASS after identity fingerprint refresh
- Fast strict: PASS, 30/30 commands, 337.406 seconds

## Known Limitations

- Existing public header candidates are broad and provisional.
- Public-header consumer compile coverage remains limited to existing tests and
  fixture scaffolding.
- No compatibility corpus, provider conformance suite, or replacement protocol
  is created by this task.
- Full CTest was not run and remains T4 full/release proof.

## Next

`DEPENDENCY-DIRECTION-01`
