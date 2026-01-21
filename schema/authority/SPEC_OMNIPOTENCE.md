# SPEC_OMNIPOTENCE (OMNI0)

Schema ID: OMNIPOTENCE
Schema Version: 1.0.0
Status: binding.
Scope: omnipotent authority definition and constraints.

## Purpose
Define omnipotence as a data-defined capability set that remains law-gated,
auditable, and scoped. Omnipotence is additive, not a bypass.

## Definition
An omnipotent authority set:
- covers all authority layers,
- is scoped by domain and time like any other capability set,
- is evaluated by the law kernel at every gate.

## Constraints (Mandatory)
- No direct mutation; all actions are explicit effects.
- All overrides are auditable and explainable.
- Archived state is read-only without a fork.
- History edits require a fork and a recorded patch.
- Negative capabilities still apply unless explicitly overridden.

## Required Explicit Effects (Canonical Tokens)
Omnipotent intents MUST resolve to explicit effects, for example:
- OP_TIME_FAST_FORWARD
- OP_TIME_SLOW_VIEW
- OP_FREEZE_SUBJECT
- OP_TRAVEL_FORCE
- OP_SPAWN_SUBJECT
- OP_TERRAIN_EDIT
- OP_FORK_TIMELINE
- OP_HISTORY_PATCH

OP_HISTORY_PATCH is fork-only and must reference the forked lineage.

## Audit Requirements
Every omnipotent effect MUST record:
- capability evidence and scope,
- law targets and scope chain,
- effect token and parameters,
- fork or archive references when relevant.

## Cross-References
- Authority layers: `schema/authority/SPEC_AUTHORITY_LAYERS.md`
- Capability taxonomy: `schema/capabilities/SPEC_CAPABILITY_TAXONOMY.md`
- Law effects: `schema/law/SPEC_LAW_EFFECTS.md`
