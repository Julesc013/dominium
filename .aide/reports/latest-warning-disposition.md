# Latest Warning Disposition

Current task: `LANGUAGE-BASELINE-01`.

## Accepted Local/Generated Warnings

- `.aide.local/**`, `.dominium.local/**`, `.xstack_cache/**`, `build/`, `out/`, `dist/`, `artifacts/`, `tmp/`, and `__pycache__/` remain local/generated roots and must not be tracked.
- Generated/archive material is not source truth unless a stronger contract explicitly promotes it.

## Language Baseline Warnings

- `python tools/validators/build/check_language_baseline.py --repo-root . --strict` reports PASS with 7 warnings and 0 errors.
- The warnings are legacy/projection presets outside active mainline:
  - `ide-win-vc6-win9x-client-gui`
  - `ide-win-vc6-nt4-server-cli`
  - `ide-win-vc71-xp-launcher-gui`
  - `ide-win-vs2015-win10-1507-1607-setup-gui`
  - `ide-mac-cw-classic-launcher-gui`
  - `ide-mac-xcode3-universal-setup-gui`
  - `ide-linux-gcc295-legacy-client-gui`

These warnings do not re-authorize C89/C++98 as the active mainline baseline.

## ABI Warnings

- `tools/validators/abi/check_public_headers.py --repo-root . --strict` still reports PASS with 2,851 warnings and 0 high-confidence violations.
- Warning classes remain provisional debt, not pass/fail suppression:
  - legacy `dom_`/`d_` public symbol and typedef prefixes;
  - unprefixed candidate public symbols and typedefs;
  - ABI-like structs missing `struct_size`;
  - C++ declarations in non-frozen public-header candidates;
  - callback-bearing structs missing explicit `void *user` context.
- These warnings block stable or frozen ABI promotion until explicitly resolved or excepted.

## Blocking Warnings

- Full CTest remains T4 full/release debt.
- Feature work and DOE-00 remain blocked until Foundation Lock closes.

Next task: `DEPENDENCY-DIRECTION-01`.
