# Pack System

Doc Version: 1

The pack system defines how packs/mods/runtime components are represented, validated, ordered, and applied to instances without affecting simulation correctness.

## Pack Manifest

A pack is described by a versioned TLV “pack manifest” that may declare:
- compatible engine/game version ranges
- dependencies (required/optional) and conflicts
- capability strings and simulation-affecting flags
- phase and explicit order
- install/verify/prelaunch task lists

Unknown tags must be skipped and preserved for forward compatibility.

See `docs/SPEC_LAUNCHER_PACKS.md`.

## Deterministic Resolution

Resolution rules are deterministic:
- ordering is stable and explicit
- tie-breakers do not depend on filesystem enumeration order
- failures/refusals are returned deterministically given the same inputs and artifacts

## Operations

Pack operations are instance-scoped and atomic:
- install / update / remove
- enable / disable
- load-order override
- prelaunch validation (tasks + simulation safety)

All operations emit audit reasons that include what changed and why.

## Simulation Safety

The launcher validates that:
- declared simulation-affecting flags are consistent with declared capabilities
- dependency constraints are satisfied
- forbidden or conflicting combinations are refused

The launcher must never silently change simulation-affecting content.

