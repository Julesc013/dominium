# Latest Dominium Status

Current task: `LANGUAGE-BASELINE-01`.

Result: PASS_WITH_WARNINGS.

## Current Green State

- Active mainline language baseline is C17 + C++17.
- Public ABI remains C-compatible; no public ABI is promoted to frozen ABI.
- Language baseline contract exists: `contracts/build/language_baseline.contract.toml`.
- Language subset schema exists: `contracts/build/language_subset.schema.json`.
- Language validators exist under `tools/validators/build/**`.
- Active CMake and verify presets now use C17/C++17.
- Fast strict gate passes: 32/32 commands in 318.25 seconds.

## Created Proof Surfaces

- `contracts/build/language_baseline.contract.toml`
- `contracts/build/language_subset.schema.json`
- `tools/validators/build/check_language_baseline.py`
- `tools/validators/build/check_cpp17_forbidden_library_use.py`
- `docs/development/LANGUAGE_BASELINE.md`
- `docs/development/C17_USAGE_POLICY.md`
- `docs/development/CPP17_USAGE_POLICY.md`
- `docs/development/MACOS_10_9_CPP17_LIBRARY_SUBSET.md`
- `docs/architecture/C_COMPATIBLE_ABI_BOUNDARY.md`
- `.aide/reports/LANGUAGE-BASELINE-01-*`
- `docs/repo/audits/LANGUAGE_BASELINE_01.md`

## Remaining Blockers

- Seven legacy IDE projection presets still declare `DOM_LANG_MODE=c89_cpp98`; they are outside active mainline.
- Existing public-header ABI warnings remain provisional stable-promotion debt.
- Full CTest remains T4 full/release proof and was not run for this task.
- Dependency direction, command surface, diagnostic/refusal registries, provider model, replacement protocol, compatibility corpus, and portability matrix remain future tasks.
- Feature implementation remains blocked until Foundation Lock closes.

DOE-00 readiness: no.

Feature implementation authorized: no.

Next task: `DEPENDENCY-DIRECTION-01`.
