# COMMAND-SURFACE-01 Initial Command Inventory

## Scope

This inventory records command-like surfaces inspected for the initial
command/result/view/event/refusal/evidence law. It is conservative and does not
claim every existing AppShell or legacy command is stable.

## Registered Now

| Command ID | Current implementation/proof path | Owner | Kind | Surfaces | Input/result known | Refusal shape known | Proof present | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `dominium.validation.run` | `tools/validators/**` umbrella | `tools.validators` | `validation` | `cli`, `headless`, `workbench`, `aide`, `test` | yes, provisional base schemas | yes, command scaffold | yes | Umbrella validation command identity only; no runtime dispatch added. |
| `dominium.repo.fast_strict.run` | `tools/test/run_fast_strict.py` | `tools.test` | `test` | `cli`, `headless`, `aide`, `test` | yes, provisional base schemas | yes, command scaffold | yes | Normal development proof gate command identity. |
| `dominium.public_surface.validate` | `tools/validators/repo/check_public_surface.py` | `tools.validators.repo` | `validation` | `cli`, `headless`, `aide`, `test` | yes, provisional base schemas | yes, command scaffold | yes | Public-surface registry validator exists and is in this task proof. |
| `dominium.abi.public_headers.validate` | `tools/validators/abi/check_public_headers.py` | `tools.validators.abi` | `validation` | `cli`, `headless`, `aide`, `test` | yes, provisional base schemas | yes, command scaffold | yes | ABI validator passes with warning debt retained. |
| `dominium.dependency_direction.validate` | `tools/validators/repo/check_dependency_directions.py` | `tools.validators.repo` | `validation` | `cli`, `headless`, `aide`, `test` | yes, provisional base schemas | yes, command scaffold | yes | Validator exists but strict result currently fails on known debt from DEPENDENCY-DIRECTION-01. |

## Inspected But Not Promoted

| Candidate | Path | Register now | Reason |
| --- | --- | --- | --- |
| AppShell command registry | `contracts/registry/command_registry.json` | no | Existing product/AppShell command registry is broad and remains outside this initial Foundation Lock command-surface scaffold. |
| AppShell command descriptor schema | `contracts/schema/command_descriptor.schema.json` | no | Useful existing surface, but this task adds a repo-wide command law rather than replacing AppShell descriptors. |
| AIDE command registry | `.aide/tools/command-registry.toml` | no | AIDE-local command registry is orchestration metadata, not product command authority. |
| Runtime shell commands/refusals docs | `docs/runtime/shell/COMMANDS_AND_REFUSALS.md` | no | Existing canonical shell doctrine remains referenced; this task does not rewrite AppShell behavior. |
| Package/content validators | `tools/package/**`, `tools/validators/**` | no | Too broad for initial command registry. Later tasks may expose package, release, diagnostic, and provider commands deliberately. |
| Workbench module command concepts | `apps/workbench/**`, docs/runtime UI docs | no | Workbench implementation is out of scope; Workbench must later call registered commands. |

## Current Classification

- initial registered commands: 5
- stable command contracts: 0
- provisional command contracts: 5
- refusal codes registered: 5
- command runtime dispatch implemented: no
- Workbench implementation changed: no
