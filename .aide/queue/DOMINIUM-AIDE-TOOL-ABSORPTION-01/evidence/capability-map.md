# Capability Map

Status: needs_review

| Capability | Existing tool candidates | Status | Future AIDE wrapper |
|---|---|---|---|
| validate | `scripts/dev/gate.py`, `validation/validation_engine.py`, `tools/xstack/ci/profiles/FAST.json`, `tools/xstack/ci/profiles/STRICT.json`, XStack validators | Found; not executed directly | `dominium.validate.fast`, `dominium.validate.strict`, `dominium.xstack.validate.bundle` |
| test | `tools/xstack/testx_all.py`, `tools/xstack/testx/**`, `scripts/dev/run_xstack_group_tests.py`, `scripts/dev/testx_proof_engine.py`, test registries | Found; wrapper-first | `dominium.testx.fast` |
| build | `CMakeLists.txt`, `CMakePresets.json`, `cmake/**`, build-like XStack tools | Found; build-sensitive | `dominium.build.native` as plan-only until explicitly authorized |
| audit | `tools/xstack/auditx/**`, `tools/xstack/auditx/**`, `docs/audit/**`, AIDE audit outputs | Found; report-only | `dominium.auditx.scan`, `dominium.docs.sanity` |
| repo_policy | `repo/repox/**`, `scripts/ci/check_repox_rules.py`, `tools/xstack/repox/**`, AIDE git/repo policy outputs | Found; authority-sensitive | `dominium.repox.rules.validate`, `dominium.xstack.status` |
| root_layout | `.aide/roots/latest-root-inventory.*`, root inventories, repo intelligence maps | Found; evidence-only | Use AIDE `roots inventory/status` plus Q52 root pilot evidence |
| docs | `docs/**`, `archive/quarantine/canon-spine/tools/xstack/auditx/README.md`, generated docs-consistency outputs | Found; doctrine-adjacent | `dominium.docs.sanity` |
| release/package | `docs/release/**`, `repo/release_policy.toml`, release/package tool candidates | Found; release-sensitive | `dominium.release.gate` as dry-run only |
| migration | migration-like scripts and schemas detected by AIDE | Found; not authorized | No execution; future reviewed migration plan required |
| security | secret scan patterns, security roots, RepoX/security-sensitive rules | Found; security-sensitive | `dominium.security.scan` with redacted evidence only |
| unknown | 854 candidates | Preserve/manual review | No execution; classify further in future phases |
