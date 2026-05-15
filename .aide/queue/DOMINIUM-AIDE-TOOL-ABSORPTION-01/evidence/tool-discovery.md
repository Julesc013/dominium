# Tool Discovery

Status: needs_review

## Searched Paths

- `.aide/**`
- `tools/**`
- `scripts/**`
- `validation/**`
- `repo/**`
- `governance/**`
- `control/**`
- `run_meta/**`
- `.xstack_cache/**` as ignored/generated evidence only
- `CMakeLists.txt`
- `CMakePresets.json`
- `cmake/**`
- command-like files matching `check_*`, `validate_*`, `audit_*`, `test_*`, `build_*`, `doctor_*`, `run_*`, `xstack`, `auditx`, `repox`, `testx`, and `buildx`

## Candidate Count

- AIDE generated inventory candidate count: 2,995.
- Dominium-specific inventory preserves all 2,995 candidates in `.aide/tools/dominium-tool-inventory.json`.
- Special-system tagged candidate counts:
  - AIDE: 195
  - AuditX: 617
  - BuildX/build-like: 10
  - RepoX: 11
  - TestX: 27
  - validation: 45
  - XStack: 196

## Key Candidate Paths

- `docs/XSTACK.md`
- `tools/xstack/**`
- `tools/auditx/**`
- `tools/xstack/auditx/**`
- `repo/repox/**`
- `scripts/repox/**`
- `scripts/ci/check_repox_rules.py`
- `tools/xstack/repox/**`
- `tools/xstack/testx/**`
- `tools/xstack/testx_all.py`
- `scripts/dev/gate.py`
- `scripts/dev/run_xstack_group_tests.py`
- `scripts/dev/testx_proof_engine.py`
- `validation/validation_engine.py`
- `CMakeLists.txt`
- `CMakePresets.json`
- `cmake/**`

## Command Matrices And Catalogs

- `tools/xstack/ci/profiles/FAST.json`
- `tools/xstack/ci/profiles/STRICT.json`
- `tools/xstack/ci/profiles/FULL.json`
- `data/registries/xstack_components.json`
- `data/registries/auditx_groups.json`
- `data/registries/testx_groups.json`
- `data/registries/testx_suites.json`
- `repo/repox/rulesets/core.json`

## Validation Reports And Generated Evidence

- `.aide/tools/latest-tool-inventory.*`
- `.aide/tools/latest-tool-classification.*`
- `.aide/tools/latest-tool-wrap-plan.*`
- `.aide/tools/latest-tool-adapter-map.*`
- `.aide/tools/tool-risk-summary.md`
- `.aide/roots/latest-root-inventory.*`
- `.aide/repo/latest-repo-intelligence.md`
- `.aide/reports/file-quality-*`

## Commands Discovered But Not Run

Legacy XStack/AuditX/RepoX/TestX commands were inspected through AIDE inventory and explain-tool where possible, but not executed directly. Direct execution remains disabled because Q51 is classification and wrapper planning only.

## Safety Notes

- `execution_allowed` is false in generated AIDE tool outputs.
- `apply_allowed` is false in Dominium-specific tool outputs.
- No unknown legacy command was run.
- No `tools/**`, `scripts/**`, `validation/**`, or `repo/**` file was modified.
