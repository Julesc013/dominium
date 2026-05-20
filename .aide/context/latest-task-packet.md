# AIDE Latest Task Packet

## PHASE

foundation-lock

## GOAL

Complete `LANGUAGE-BASELINE-01` by moving Dominium active mainline governance,
build settings, validators, and documentation to C17 + C++17 while preserving a
C-compatible public ABI and restricted C++17 library subset for macOS 10.9.5.

## WHY

The active OS floor is Windows 7 SP1, macOS 10.9.5, and Linux. C90/C++98 is no
longer the right mainline implementation constraint, but public ABI and
determinism rules must remain explicit and portable.

## CONTEXT_REFS

- `AGENTS.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `contracts/testing/test_tiers.contract.toml`
- `contracts/public_surface/public_surface.contract.toml`
- `contracts/abi/c_api.contract.toml`
- `contracts/abi/language_boundary.contract.toml`
- `.aide/context/latest-context-packet.md`

## ALLOWED_PATHS

- `contracts/build/**`
- `contracts/abi/**` for language-floor updates
- `contracts/public_surface/**` for language baseline registration
- `contracts/testing/**` for fast-strict language validators
- `docs/architecture/**` language/ABI policy docs
- `docs/development/**` language policy docs
- `tools/validators/build/**`
- CMake and preset files needed for C17/C++17 build enforcement
- `tests/contract/**` and `tests/invariant/**` language proof fixtures/scripts
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/audits/**`

## FORBIDDEN_PATHS

- `.dominium.local/**`
- `.aide.local/**`
- build, projection, release, installer, upload, cache, and generated output roots
- gameplay, renderer, Workbench UI, native GUI, worldgen, package runtime, and product behavior implementation paths

## IMPLEMENTATION

- Add language baseline contract and schema.
- Add C17/C++17 validators.
- Update active CMake and presets to C17/C++17.
- Update API/ABI/public-surface/test-tier policy references.
- Record legacy projection warnings without re-authorizing the old mainline floor.

## VALIDATION

- Python py_compile for new language validators and scripts.
- JSON parse for touched schemas/registries.
- Language baseline validator strict/json.
- C++17 restricted library validator strict/json.
- Test-tier, public-surface, and public-header ABI validators.
- `cmake --preset verify`.
- `cmake --build --preset verify --target ALL_BUILD`.
- `python tools/test/run_fast_strict.py --repo-root .`.
- git diff checks.

## COMMITS

Commit subject: `audit(build): move mainline to c17 cpp17`

## EVIDENCE

- `.aide/reports/LANGUAGE-BASELINE-01-status.md`
- `.aide/reports/LANGUAGE-BASELINE-01-validation.md`
- `.aide/reports/LANGUAGE-BASELINE-01-results.json`
- `.aide/reports/LANGUAGE-BASELINE-01-language-inventory.md`
- `.aide/reports/LANGUAGE-BASELINE-01-fast-strict.json`
- `.aide/reports/LANGUAGE-BASELINE-01-fast-strict.md`
- `docs/repo/audits/LANGUAGE_BASELINE_01.md`

## NON_GOALS

No feature implementation, public release, tag, upload, renderer/native GUI
behavior, package runtime change, provider model, dependency direction law,
compatibility corpus, or full CTest proof.

## ACCEPTANCE

Language contract and validators exist, active build surfaces use C17/C++17,
fast strict passes, and feature work stays blocked pending Foundation Lock.

## OUTPUT_SCHEMA

Final report includes branch, starting HEAD, ending HEAD, origin/main, push
status, result, created files, validator status, fast strict status, known
warnings, worktree status, and next task.
