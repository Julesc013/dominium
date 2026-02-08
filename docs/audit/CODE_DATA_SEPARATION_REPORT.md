Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# IRC-0 Phase 1: Code vs Data Separation Report

## Scope

- Engine, game, appcore, launcher, setup, client, server, tools.
- Classification targets: enforcement logic, policy logic, configuration logic.
- Constraint: no semantic changes.

## Classification Summary

| Subsystem | Enforcement logic (code) | Policy logic (code) | Configuration/data logic |
| --- | --- | --- | --- |
| `engine/` | `engine/modules/core/process_guard.c` mutation guard instrumentation | kernel and scheduling gate choices under deterministic policy | schema-driven inputs consumed via validators and registries |
| `game/` | refusal paths and deterministic guard checks in rule pipelines | rule-level command behavior and refusal mapping | scenario and pack data under `data/` + `schema/` |
| `libs/appcore/` | command metadata validation, capability checks | canonical command descriptors in `libs/appcore/command/command_registry.c` | generated UI binding tables in `libs/appcore/ui_bind/` |
| `tools/` | `tools/pack/pack_validate.py`, `tools/ui_bind/ui_bind_main.cpp`, RepoX scripts | tool command routing policies | schema and manifest validation surfaces |
| `launcher/ setup/ client/ server/ tools host` | CLI validation and refusal exits | command parsing and UI mode policies | runtime inputs via CLI flags + manifest/state files |

## Enforcement Points Confirmed

- Pack capability gating is enforced in schema and validator:
  - `schema/pack_manifest.schema`
  - `tools/pack/pack_validate.py`
- Stage/progression field rejection exists in pack validation:
  - `tools/pack/pack_validate.py` (`forbidden_stage_fields`)
- Process-only mutation guard exists:
  - `engine/include/domino/core/process_guard.h`
  - `engine/modules/core/process_guard.c`
- UI binding contract enforcement exists:
  - `tools/ui_bind/ui_bind_main.cpp`

## Clear Misplacements / Drift Risks

1. Canonical command registry is not the runtime command source for app CLIs.
   - Registry exists in `libs/appcore/command/command_registry.c`.
   - Runtime CLIs still contain direct command/help surfaces (example: `client/app/main_client.c`).
   - Impact: command graph drift risk between appcore registry and product binaries.

2. Dispatch path is declared but not used as a shared execution surface.
   - Stub remains in `libs/appcore/command/command_dispatch.c` (`return -1`).
   - `appcore_dispatch_command` is not used by runtime app binaries (only scaffold contract checks reference it).
   - Impact: layered architecture contract is documented but only partially enforced in runtime wiring.

3. Intentional stubs remain in UI backends and selected app shells.
   - Win32 shared UI stubs under `libs/ui_backends/win32/src/*_stub.c`.
   - Setup/server GUI and TUI intentionally refuse in current runtime paths.
   - Impact: acceptable for now, but limits parity claims to refusal-level behavior.

## Data Assuming Code Behavior

- `schema/pack_manifest.schema` requires both `depends` and `requires_capabilities`.
- `tools/pack/pack_validate.py` enforces equivalence between these fields.
- This is deterministic and explicit, but duplication means pack authors rely on validator reconciliation rules.

## Mechanical Fixes Applied in Phase 1

- None.
- Reason: identified issues are architectural wiring gaps, not safe mechanical relocations.

## Phase 1 Conclusion

- Core code/data boundary enforcement exists and is active.
- Canonical command graph adoption remains partial in runtime CLIs.
- No safe behavior-preserving mechanical relocation was available in this phase.
