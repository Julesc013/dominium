# Dominium Tool Capability Map

Status: needs_review

| Capability | Existing Tool Families | Q51 Status | Future Wrapper Direction |
|---|---|---|---|
| validate | XStack profiles, gate scripts, validation engine | Found | `dominium.validate.fast`, `dominium.validate.strict` |
| test | TestX, test registries, group test runners | Found | `dominium.testx.fast` |
| build | CMake, build-like XStack surfaces | Found | `dominium.build.native` plan-only |
| audit | AuditX, docs/audit surfaces | Found | `dominium.auditx.scan` |
| repo_policy | RepoX, AIDE git/repo policy outputs | Found | `dominium.repox.rules.validate` |
| root_layout | AIDE roots inventory and repo intelligence | Found | Q52 evidence-only root pilot |
| docs | Docs/audit tooling and consistency reports | Found | `dominium.docs.sanity` |
| release/package | Release policy and packaging candidates | Found | `dominium.release.gate` dry-run only |
| migration | Migration-like candidates | Found | No execution; future reviewed plan |
| security | Security roots, secret-scan patterns, RepoX rules | Found | `dominium.security.scan` redacted report-only |
| unknown | 854 candidates | Preserve/manual review | Further classification before execution |
