# API-ABI-CANON-01 Public Header Inventory

Task: `API-ABI-CANON-01`
Date: 2026-05-20
Starting HEAD: `b923e306bba40b1d7d147f3395f18851fbfc4cf4`
origin/main at start: `3eb4b7c4f7e230e0384547d94673148003fc2d93`

## Candidate Roots

| Root | Owner | Classification | Candidates | Register now | Notes |
| --- | --- | --- | ---: | --- | --- |
| `engine/include` | `engine` | candidate public reusable headers | 109 | yes | Provisional Domino public header surface; no frozen ABI claim. |
| `runtime/include` | `runtime` | candidate public runtime headers | 34 | yes | Provisional runtime header surface; platform-specific surfaces still need later provider/platform classification. |
| `game/include` | `game` | candidate Dominium game/product headers | 222 | yes | Provisional; includes broad domain and some C++-visible implementation-boundary headers. |
| `apps/launcher/include` | `apps.launcher` | internal product include tree | 8 | already registered internal | Not stable public API. |
| `apps/setup/include` | `apps.setup` | internal product include tree | 2 | already registered internal | Not stable public API. |
| `contracts/abi/dom_contracts/include` | `contracts.abi` | existing ABI contract header tree | not scanned by default | defer | Existing contract headers remain outside this new default validator path until a later ABI table/symbol task decides whether to register them as public ABI. |
| `tests/contract/public_headers` | `tests.contract` | fixture-only | 3 headers + 1 C consumer | yes | Fixture suite for validator behavior; not a product surface. |

## Validator Summary

Command:

```powershell
python tools/validators/abi/check_public_headers.py --repo-root . --strict
```

Result: PASS.

- public header candidates inspected: 375
- high-confidence violations: 0
- warning findings: 2,851
- registered stability inspected:
  - `provisional`: 365
  - `internal`: 10

## Warning Breakdown

The warning count is deliberately visible and blocks stable/frozen promotion:

| Code | Count | Disposition |
| --- | ---: | --- |
| `legacy_public_symbol_prefix` | 1,201 | Existing `dom_`/`d_` symbols remain provisional and require exception or replacement before stable promotion. |
| `unprefixed_public_symbol` | 1,148 | Candidate public declarations need prefix review before stable promotion. |
| `abi_struct_without_struct_size` | 239 | ABI-like structs need `struct_size` before stable ABI promotion unless explicitly exempted. |
| `unprefixed_public_typedef` | 106 | Candidate typedef names need prefix review before stable promotion. |
| `legacy_public_typedef_prefix` | 101 | Existing `dom_`/`d_` typedefs remain provisional. |
| `cpp_public_abi` | 34 | C++ declarations exist in non-frozen public-header candidates; they cannot be stable C ABI without reclassification. |
| `callback_without_user_pointer` | 22 | Callback-bearing structs need explicit `void *user` context before stable promotion. |

## Obvious Risks

- No platform-header leak was found in `engine/include` by the validator.
- Existing broad header surfaces are not renamed or rewritten by this task.
- Public header consumer compilation remains governed by existing `tests/contract/public_header_c89_compile.py` and `tests/contract/public_header_cpp98_compile.py`; deeper compatibility corpus is future full/release proof.
