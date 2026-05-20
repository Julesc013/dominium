# CAPABILITY-REFUSAL-LAW-01 Initial Capability Inventory

Starting HEAD: `6fef00a6f16488844984eb64e0305aee54a738ca`

Inventory command:

`python tools/validators/contracts/check_capability_refusal.py --repo-root . --inventory`

Result: `warning`

The inventory is descriptive only. CAPABILITY-REFUSAL-LAW-01 does not migrate
providers, runtime backends, package behavior, Workbench modules, or product
features.

## Summary

- files scanned: 17,837
- capability candidates: 86
- provider candidates: 66
- future provider-model items: 97
- command-required capability candidates: 6
- artifact/trust candidates: 650
- deferred provider/AIDE/release-adjacent files: 285
- total classified candidates: 1,190

## Examples

Capability candidates:

- `runtime/audio/audio.c`
- `runtime/input/input.c`
- `runtime/network/d_net.c`

Provider candidates:

- `runtime/platform/platform_audio.py`
- `runtime/platform/platform_caps_probe.py`
- `runtime/platform/platform_gfx.py`
- `runtime/platform/platform_input.py`

Future provider-model items:

- `apps/workbench/module/domain/universe/ue_commands.cpp`
- `apps/workbench/module/domain/universe/ue_queries.h`

Command-required capability candidates:

- `contracts/command/command_surface.contract.toml`
- `contracts/refusal/refusal_code.registry.json`

Artifact/trust candidates:

- `content/packs/README.md`
- `content/packs/blueprint/blueprints.default.m1/pack.capabilities.json`

Deferred items include existing AIDE provider/catalog surfaces and future
provider-model inputs. They are not runtime authority.

## Deferred Work

- PROVIDER-MODEL-01 owns provider declaration and conformance law.
- MOD-PACK-TRUST-MODEL-01 owns deeper mod/pack trust policy.
- No current provider, renderer, platform, package, or Workbench implementation
  is changed by this task.
