Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# MOVE-FAMILY-00C-PLAN Import Map

## Summary

| Root | Active Python Import Files | Path Reference Files |
| --- | ---: | ---: |
| `validation` | 8 | 1662 |
| `meta` | 104 | 482 |
| `governance` | 9 | 679 |
| `performance` | 4 | 137 |

Path-reference counts include high-volume AIDE, audit, generated, and historical evidence. They are not all active rewrite targets.

## Decision-Bearing Import Consumers

| Group | Consumers |
| --- | --- |
| `validation` | `runtime/shell/commands/command_engine.py`, `compat/shims/validation_shims.py`, `tools/validators/suite/tool_run_validation.py`, `tools/convergence/convergence_gate_common.py`, `tools/xstack/repox/check.py`, AuditX, TestX |
| `meta.identity` | release, security/trust, lib install/instance/save validators, archive/generated/dist/setup/MVP/meta tools, validation, TestX |
| `meta.stability` | validation, governance tools, AuditX analyzers, convergence, release, review, security, RepoX, TestX |
| `governance` | release/update resolver, archive/generated/dist/setup tools, release tools, governance tools, TestX |
| semantic/runtime `meta` | engine time, game domains, runtime/session, tools, invariant tests, TestX |
| `performance` | client interaction, game materials, XStack session runtime |

## Rewrite Posture

- Apply-phase rewrites in this task: none.
- Future validation/identity/stability rewrites require a shim contract and consumer smoke checks.
- Future governance rewrites require release-control import proof.
- Performance and semantic `meta` rewrites are deferred to separate runtime/domain ownership plans.

## Historical References

Historical AIDE/root-recycling/audit/generated references should not be rewritten by a future active-tool apply unless that apply explicitly targets evidence refresh.
