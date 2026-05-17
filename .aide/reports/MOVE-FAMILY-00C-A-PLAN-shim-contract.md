Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# MOVE-FAMILY-00C-A-PLAN Shim Contract

## Contract

Temporary shims are planned, not created.

Shim behavior must be:

- import/re-export only;
- no file writes;
- no subprocess calls;
- no environment mutation;
- no runtime warning emission;
- no new semantics;
- no behavior mutation.

## Planned Shims

| Old Import | New Import | Shim Files | Temporary Old-Import Callers |
| --- | --- | --- | --- |
| `validation` | `tools.validators.validation` | `validation/__init__.py`, `validation/validation_engine.py` | `compat/shims/validation_shims.py`, `runtime/appshell/commands/command_engine.py` |
| `meta.identity` | `tools.validators.identity` | `meta/identity/__init__.py`, `meta/identity/identity_validator.py` | `lib/install/install_validator.py`, `lib/instance/instance_validator.py`, `lib/save/save_validator.py`, `release/release_manifest_engine.py`, `release/update_resolver.py`, `security/trust/license_capability.py` |
| `meta.stability` | `tools.validators.stability` | `meta/stability/__init__.py`, `meta/stability/stability_scope.py`, `meta/stability/stability_validator.py` | `compat/shims/common.py`, `tools/governance/governance_model_common.py` |

## Retirement

Each shim requires a later retirement task after active callers are rewritten or receive owner-specific wrappers. New old imports must be forbidden by the planned static check.
