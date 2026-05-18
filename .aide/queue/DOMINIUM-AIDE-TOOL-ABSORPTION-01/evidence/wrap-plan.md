# Wrap Plan

Status: needs_review

Q51 plans wrappers only. It does not create executable legacy-tool wrappers, does not run unknown tools, and does not approve mutation.

| Future Wrapper ID | Source Tool Path | Proposed AIDE Command Name | Input / Output Contract Hint | Validation Requirement | Risk Notes |
|---|---|---|---|---|---|
| `dominium.xstack.status` | `docs/XSTACK.md`, `tools/xstack/run.py`, `scripts/dev/gate.py` | `tools run dominium.xstack.status --dry-run` | Input: repo snapshot. Output: XStack status evidence. | Prove report-only behavior before enabling. | Legacy governance/tooling system. |
| `dominium.xstack.validate.bundle` | `tools/xstack/bundle_validate.py`, `tools/xstack/ci/xstack_ci_entrypoint.py` | `tools run dominium.xstack.validate.bundle --dry-run` | Input: explicit bundle/profile. Output: validation evidence. | Prove safe args and side effects. | Validation/build-sensitive. |
| `dominium.auditx.scan` | `tools/xstack/auditx/auditx.py`, `tools/xstack/auditx/check.py` | `tools run dominium.auditx.scan --dry-run` | Input: scoped audit group. Output: audit findings under `.aide/tools/`. | Keep generated findings as evidence only. | Doctrine/release-adjacent. |
| `dominium.repox.rules.validate` | `scripts/ci/check_repox_rules.py`, `repo/repox/rulesets/core.json` | `tools run dominium.repox.rules.validate --dry-run` | Input: RepoX ruleset and repo snapshot. Output: policy validation report. | Confirm read-only behavior before execution. | Authority-sensitive. |
| `dominium.testx.fast` | `tools/xstack/testx_all.py`, `tools/xstack/testx/**`, `scripts/dev/run_xstack_group_tests.py` | `tools run dominium.testx.fast --dry-run` | Input: named safe TestX suite. Output: test evidence. | Classify runtime and duration first. | Broad test runner risk. |
| `dominium.validate.fast` | `scripts/dev/gate.py`, `validation/validation_engine.py`, FAST profile | `validate dominium.fast --dry-run` | Input: FAST validation profile. Output: pass/fail evidence. | Confirm documented non-mutating quick command. | Candidate only. |
| `dominium.validate.strict` | `scripts/dev/gate.py`, STRICT profile | `validate dominium.strict --dry-run` | Input: STRICT validation profile. Output: validation evidence. | Future opt-in after duration proof. | Potentially expensive. |
| `dominium.build.native` | `CMakeLists.txt`, `CMakePresets.json`, `cmake/**` | `build dominium.native --plan-only` | Input: CMake preset. Output: build plan. | Never clean/package by default. | Build-sensitive. |
| `dominium.docs.sanity` | `docs/**`, AuditX docs checks | `docs dominium.sanity --dry-run` | Input: docs scope. Output: consistency evidence. | Respect AGENTS/canon authority order. | Doctrine-adjacent. |
| `dominium.security.scan` | `security/**`, local secret scan patterns | `security dominium.scan --dry-run` | Input: local paths. Output: redacted warnings. | No raw secrets in evidence. | Security-sensitive. |
| `dominium.release.gate` | `repo/release_policy.toml`, `docs/release/**` | `release dominium.gate --dry-run` | Input: release gate profile. Output: readiness evidence. | Future release-control scope required. | Release-sensitive. |

All wrappers are future-phase required and have `execution_allowed: false` in Q51.
