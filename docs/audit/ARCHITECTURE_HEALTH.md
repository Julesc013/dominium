# Architecture Health

Status: AT RISK (BLOCKED)
Confidence: LOW

## Long-term assessment
The repository contains canonical architectural docs and schema definitions,
but the runtime codebase does not yet enforce the core invariants. Legacy
package systems and strict schema tooling conflict with the forward-compatible,
capability-driven model. As a result, the system is not yet a stable kernel for
decades-long world building.

## Strengths
- Canonical architecture, terminology, and compatibility docs exist under
  `docs/architectureitecture/`.
- UPS registry implementation is deterministic and zero-pack safe in isolation
  (`engine/modules/ups/d_ups.c`).
- Domain volume runtime and tests exist (`engine/modules/world/domain_volume.cpp`,
  `engine/tests/domain_volume_tests.cpp`).

## Critical gaps
- UPS is not integrated into engine/game startup; legacy package systems remain
  active (`engine/modules/core/pkg.c`, `engine/modules/mod/package_registry.c`).
- Authority tokens, process execution enforcement, and snapshots are declared
  but not implemented or used.
- Coredata tooling rejects unknown fields/tags, violating forward-compatibility
  requirements.
- Documentation coherence is broken by unarchived legacy specs under
  `docs/architecture` and `docs/specs`.

## Known limitations
- Zero-asset boot is not verified end-to-end.
- Save/replay compatibility modes are not selected or exposed at runtime.
- Mod supersession and sandboxing are not enforced.

## Required remediation (non-exhaustive)
- Wire UPS capability resolution into engine/game startup and content access.
- Enforce authority token validation for all mutations.
- Route all state changes through process execution with audit hooks.
- Implement snapshot creation and immutable querying.
- Relax coredata tooling to preserve unknown fields and tags.
- Archive or mark legacy docs to eliminate contradictions.
