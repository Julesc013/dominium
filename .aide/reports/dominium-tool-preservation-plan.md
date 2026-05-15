# Dominium Tool Preservation Plan

Status: needs_review

Preservation law for Q51 and Q52:

`discover -> classify -> map capability -> plan wrapper -> preserve -> future adapt/migrate/retire only with evidence`

## Preserve By Default

- XStack: `docs/XSTACK.md`, `tools/xstack/**`, registries, profiles, and gate scripts.
- AuditX: `tools/auditx/**`, `tools/xstack/auditx/**`, audit docs and registries.
- RepoX: `repo/repox/**`, `scripts/repox/**`, `scripts/ci/check_repox_rules.py`, RepoX rules.
- TestX: `tools/xstack/testx/**`, `tools/xstack/testx_all.py`, TestX scripts, registries, docs, and tests.
- Build/validation surfaces: `CMakeLists.txt`, `CMakePresets.json`, `cmake/**`, `validation/**`, documented validation profiles.

## Execution Policy

Legacy tools are not execution-enabled by Q51. Future wrappers must prove:

- command contract;
- input/output locations;
- timeout and resource expectations;
- mutation behavior;
- generated evidence path;
- validation command and expected result.

## Retirement Policy

No tool retirement is approved until useful checks are wrapped or migrated with evidence and a future reviewed task explicitly authorizes reference updates and cleanup.
