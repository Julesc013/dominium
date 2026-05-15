# XStack Wrapper Registry

Status: generated plan-only registry

| System | Present | Matched Paths | Wrapper ID | AIDE Command | Capabilities | Risk | Execution |
|---|---:|---:|---|---|---|---|---|
| XStack | True | 1935 | `dominium.xstack.status` | `xstack status` | validate, audit, repo_policy, context | authority_sensitive | disabled |
| AuditX | True | 633 | `dominium.auditx.status` | `xstack status --system auditx` | audit, docs, repo_policy, security | authority_sensitive | disabled |
| RepoX | True | 44 | `dominium.repox.policy` | `xstack status --system repox` | repo_policy, validate, security, release | authority_sensitive | disabled |
| TestX | True | 1821 | `dominium.testx.status` | `xstack status --system testx` | test, validate | build_sensitive | disabled |
| BuildX-like build wrappers | True | 35 | `dominium.buildx.status` | `xstack status --system buildx` | build, package, validate | build_sensitive | disabled |
| FAST/STRICT/FULL validation profiles | True | 299 | `dominium.validation.profiles` | `xstack status --system validation_profiles` | validate, test, audit | build_sensitive | disabled |

## Enablement Gate

Execution remains disabled. A future wrapper task must prove command side effects, timeout, output paths, and validation before any wrapper can run a legacy tool.
