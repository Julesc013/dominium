# XStack AIDE Integration

Status: added, no-apply

## Added AIDE Command Family

`aide_lite.py` now supports:

- `xstack status`
- `xstack wrap-plan`
- `xstack validate`

These commands inspect and validate AIDE-local integration artifacts only. They do not execute XStack, AuditX, RepoX, TestX, BuildX, validation profiles, or any legacy tool command.

## Generated Artifacts

- `.aide/tools/xstack-integration-contract.json`
- `.aide/tools/xstack-integration-contract.md`
- `.aide/tools/xstack-wrapper-registry.json`
- `.aide/tools/xstack-wrapper-registry.md`
- `.aide/tools/xstack-integration-status.md`
- `.aide/reports/dominium-xstack-aide-integration.md`

## Wrapper Families

- `dominium.xstack.status`
- `dominium.auditx.status`
- `dominium.repox.policy`
- `dominium.testx.status`
- `dominium.buildx.status`
- `dominium.validation.profiles`

Every wrapper has `execution_allowed: false`, `apply_allowed: false`, and `no_apply: true`.

## Validation

`aide_lite.py xstack validate`: PASS

## Future Work

The next Dominium-local development task should convert the registry into executable wrappers one-by-one only after proving command lines, side effects, output paths, timeouts, and preservation boundaries.
