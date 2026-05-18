# Existing Tool Systems

## XStack/AuditX/RepoX/TestX-Like Systems Found

- XStack: `docs/XSTACK.md`, `tools/xstack/**`, `data/registries/xstack_components.json`, `scripts/dev/gate.py`.
- AuditX: `tools/xstack/auditx/**`, `tools/xstack/auditx/**`, `docs/audit/auditx/**`, `data/registries/auditx_groups.json`.
- RepoX: `repo/repox/**`, `scripts/repox/**`, `scripts/ci/check_repox_rules.py`, `docs/repox/**`, `docs/audit/repox/**`, `tools/xstack/repox/**`.
- TestX: `tools/xstack/testx/**`, `tools/xstack/testx_all.py`, `scripts/dev/testx_proof_engine.py`, `scripts/dev/run_xstack_group_tests.py`, `data/registries/testx_groups.json`, `data/registries/testx_suites.json`, `docs/audit/testx/**`, `tests/testx/**`.
- BuildX/build control: `tools/build/**`, `CMakeLists.txt`, `CMakePresets.json`, `scripts/ci/run_strict_build_and_annotate.py`, `docs/guides/BUILDING.md`.
- Compat/Control/Governance families: `tools/xstack/compatx/**`, `tools/xstack/controlx/**`, `tools/governance/**`, `validation/validation_engine.py`, `control/**`, `governance/**`.

## Capability Families

- validate: `validation/validation_engine.py`, `tools/ci/validate_all.py`, `tools/ci/validate_*.py`, `tools/domain/tool_domain_validate.py`, `tools/validators/core/tool_graph_validate.py`, `tools/xstack/compatx/core/semantic_contract_validator.py`, CMake `verify_fast`.
- test: `tools/xstack/testx_all.py`, `tools/xstack/testx/tests/**`, `scripts/dev/run_xstack_group_tests.py`, CMake `testx_fast`, `testx_verify`, `testx_dist`, `testx_all`.
- build: `CMakePresets.json`, `CMakeLists.txt`, `tools/build/**`, CMake verify presets, tuple build helpers.
- audit: `tools/xstack/auditx/auditx.py`, `tools/xstack/auditx/analyzers/**`, `docs/audit/**`.
- repo_policy: `repo/repox/rulesets/**`, `scripts/ci/check_repox_rules.py`, `contracts/repo/**`.
- docs: `scripts/verify_docs_sanity.py`, docs governance/audit maps.
- release: `repo/release_policy.toml`, `docs/release/**`, `tools/package/distribution/**`, release/update/security roots.
- package: CMake `dist_*` and `pkg_verify_all` targets, `tools/package/distribution/**`.
- migration: `tools/compat/**`, `tools/xstack/compatx/**`, `contracts/install/**`, `contracts/release/**`.
- unknown/legacy: numerous `tool_*`, `verify_*`, `run_*`, `check_*` wrappers requiring later inventory before wrapping or retirement.

## Commands Discovered But Not Run

- `python scripts/dev/gate.py verify --repo-root .`.
- `python scripts/dev/gate.py strict --repo-root .`.
- `python scripts/dev/gate.py full --repo-root .`.
- `python tools/xstack/auditx/auditx.py scan --repo-root .`.
- `python tools/xstack/auditx/auditx.py verify --repo-root .`.
- `python scripts/dev/run_xstack_group_tests.py --repo-root . --group-id ...`.
- `python scripts/ci/check_repox_rules.py ...`.
- CMake configure/build/test presets including `cmake --preset verify` and `cmake --build --preset verify`.

These commands were not run in Q49 because they can write `.xstack_cache`, `docs/audit/**`, build directories, generated reports, or product validation outputs. They are valid future Q50/Q51 validation candidates only with explicit scope.

## Preservation Rule

Q50 and later AIDE work must follow:

`discover -> classify -> wrap -> adapt -> migrate -> retire with evidence`

No deletion, rename, move, replacement, or absorption of existing Dominium tools is authorized by Q49.

## Q51 Implication

Q51 should inventory and classify tool systems separately, preferably producing an AIDE tool inventory and wrapper/absorption plan for XStack, AuditX, RepoX, TestX, validation, build, release, package, migration, docs, and unknown/legacy tool families.
