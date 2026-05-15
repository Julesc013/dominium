# Dominium Tool Wrap Plan

Status: generated Q51 plan-only artifact

Q51 does not execute, delete, rename, move, migrate, or retire existing Dominium tools. Every wrapper below is future-phase only and has `execution_allowed: false`.

| Wrapper ID | Source Paths | Proposed AIDE Command | Capabilities | Risk / Validation |
|---|---|---|---|---|
| `dominium.xstack.status` | docs/XSTACK.md<br>tools/xstack/run.py<br>scripts/dev/gate.py | `tools run dominium.xstack.status --dry-run` | repo_policy, validate, audit | XStack is a legacy governance/tooling system; wrapper-first only. Validation: Must be proven non-mutating before execution is enabled. |
| `dominium.xstack.validate.bundle` | tools/xstack/bundle_validate.py<br>tools/xstack/bundle_validate<br>tools/xstack/ci/xstack_ci_entrypoint.py | `tools run dominium.xstack.validate.bundle --dry-run` | validate, repo_policy | May touch validation/build assumptions; execution remains disabled in Q51. Validation: Q52+ must prove safe arguments and side effects before enabling. |
| `dominium.auditx.scan` | tools/auditx/auditx.py<br>tools/auditx/README.md<br>tools/xstack/auditx/check.py | `tools run dominium.auditx.scan --dry-run` | audit, docs, repo_policy | Audit surfaces may reference protected doctrine and release policy. Validation: Must separate generated evidence from canonical doctrine. |
| `dominium.repox.rules.validate` | scripts/ci/check_repox_rules.py<br>repo/repox/rulesets/core.json<br>tools/xstack/repox/check.py | `tools run dominium.repox.rules.validate --dry-run` | repo_policy, validate, security | Repo policy tooling is authority-sensitive and branch-sensitive. Validation: Must confirm rule checker is read-only before wrapper execution. |
| `dominium.testx.fast` | tools/xstack/testx_all.py<br>tools/xstack/testx/README.md<br>scripts/dev/run_xstack_group_tests.py<br>scripts/dev/testx_proof_engine.py | `tools run dominium.testx.fast --dry-run` | test, validate | Do not execute broad historical test runners until safe profile is proven. Validation: Must classify runtime/build side effects and expected duration. |
| `dominium.validate.fast` | scripts/dev/gate.py<br>validation/validation_engine.py<br>tools/xstack/ci/profiles/FAST.json | `validate dominium.fast --dry-run` | validate | Candidate wrapper only; not executed in Q51. Validation: Confirm the documented FAST command is non-mutating and quick. |
| `dominium.validate.strict` | scripts/dev/gate.py<br>tools/xstack/ci/profiles/STRICT.json<br>validation/validation_engine.py | `validate dominium.strict --dry-run` | validate, test, audit | May be expensive or broad; keep disabled until proven. Validation: Must be opt-in after duration and mutation risk are documented. |
| `dominium.build.native` | CMakeLists.txt<br>CMakePresets.json<br>cmake | `build dominium.native --plan-only` | build | Build-sensitive; Q51 records only. Validation: Never run clean/package by default; build execution requires explicit future scope. |
| `dominium.docs.sanity` | docs<br>scripts<br>tools/auditx/README.md | `docs dominium.sanity --dry-run` | docs, audit | Doctrine-adjacent; report-only by default. Validation: Must respect AGENTS.md and canon authority ordering. |
| `dominium.security.scan` | security<br>scripts<br>tools | `security dominium.scan --dry-run` | security, audit | Security-sensitive; require redaction and no provider calls. Validation: No raw secrets in committed evidence. |
| `dominium.release.gate` | repo/release_policy.toml<br>docs/release | `release dominium.gate --dry-run` | release, package, repo_policy | Release-sensitive; Q51 wrapper plan only. Validation: Future release-control task required before any active release action. |

## Source Inventory Summary

- Tool candidates: 2995
- Unknown candidates: 854
- High-risk candidates: 171
- Fate counts: {'wrap': 2140, 'unknown': 854, 'keep': 1}
- Capability counts: {'validate': 206, 'test': 234, 'release': 158, 'audit': 1040, 'repo_policy': 251, 'context': 204, 'unknown': 854, 'install': 170, 'package': 206, 'generate': 126, 'docs': 465, 'build': 225, 'lint': 3, 'format': 42, 'migrate': 6, 'security': 18}

## Preservation Rule

Do not delete, rename, move, or retire XStack/AuditX/RepoX/TestX until useful checks are wrapped or migrated with evidence.
