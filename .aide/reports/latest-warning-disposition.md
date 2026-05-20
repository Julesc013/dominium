# Latest Warning Disposition

Current task: `API-ABI-CANON-01`.

## Accepted Local/Generated Warnings

- `.aide.local/**`, `.dominium.local/**`, `.xstack_cache/**`, `build/`, `out/`, `dist/`, `artifacts/`, `tmp/`, and `__pycache__/` remain local/generated roots and must not be tracked.
- Generated/archive material is not source truth unless a stronger contract explicitly promotes it.

## ABI Warnings

- `tools/validators/abi/check_public_headers.py --repo-root . --strict` reports PASS with 2,851 warnings and 0 high-confidence violations.
- Warning classes are provisional debt, not pass/fail suppression:
  - legacy `dom_`/`d_` public symbol and typedef prefixes;
  - unprefixed candidate public symbols and typedefs;
  - ABI-like structs missing `struct_size`;
  - C++ declarations in non-frozen public-header candidates;
  - callback-bearing structs missing explicit `void *user` context.
- These warnings block stable or frozen ABI promotion until explicitly resolved or excepted.

## Conservative Classifications

- Engine, runtime, and game header surfaces remain `provisional`, not frozen ABI.
- Launcher/setup header trees remain `internal`.
- ABI canon, language-boundary contract, ABI rule registry, and public-header schema are `provisional`.
- Public-header fixtures are `fixture`.

## Blocking Warnings

- Compatibility corpus and deeper public-header consumer compilation remain later full/release proof work.
- No provider ABI, command contract, or module API is stable yet.
- Full CTest remains T4 full/release debt.
- Feature work and DOE-00 remain blocked until Foundation Lock closes.

Next task: `DEPENDENCY-DIRECTION-01`.
