# XStack AIDE Integration Contract

Status: plan-only no-apply integration contract

This contract integrates Dominium's XStack/AuditX/RepoX/TestX-like systems into AIDE as preserved, modular wrapper candidates. It does not execute, delete, rename, move, migrate, retire, or replace legacy systems.

## Boundaries

- no_apply: True
- execution_allowed: False
- apply_allowed: False
- provider_or_model_calls: forbidden
- network_calls: forbidden
- legacy_tool_execution: disabled_by_default

## AIDE Command Family

- `xstack status`: inspect the registry and preservation posture.
- `xstack wrap-plan`: regenerate contract, registry, and reports without executing legacy tools.
- `xstack validate`: validate no-apply boundaries and wrapper registry consistency.

## Summary

- systems modeled: 6
- systems detected: 6
- wrapper plans: 6

## Preservation Rule

Do not delete, rename, move, retire, or replace XStack/AuditX/RepoX/TestX until useful checks are wrapped or migrated with evidence.
