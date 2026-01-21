# SPEC_AUTHORITY_LAYERS (OMNI0)

Schema ID: AUTHORITY_LAYERS
Schema Version: 1.0.0
Status: binding.
Scope: canonical authority layers and separation rules.

## Purpose
Define independent authority layers so spectator, competitive, anarchy, and
omnipotent control are expressed via the same primitives and law gate.

## Authority Layers (Independent)
Each capability grants power in one or more layers. No layer implies another.

- SIMULATION: authoritative state mutation (spawn, destroy, build, transfer).
- TEMPORAL: time perception and scheduling controls (view dilation, freeze).
- SPATIAL: movement, entry, and boundary permissions across domains.
- EPISTEMIC: information access, inspection, and visibility of hidden state.
- GOVERNANCE: law, jurisdiction, and capability policy modification.
- EXECUTION: backend selection, budgets, and determinism policy controls.
- INTEGRITY: validation, anti-cheat policy, and client/tool admission.
- ARCHIVAL: history access, freeze, fork, and archival mutation controls.

## Layer Independence Rules
- Capabilities MUST declare their layer coverage.
- Absence of a capability is not a denial; denials are explicit.
- Negative capabilities take precedence unless explicitly overridden.
- Omnipotence is the union of layers, not a bypass of law.

## Intent -> Action -> Effect (Mandatory)
All power follows the same sequence:
1) Intent (declared capability and law targets).
2) Law Gate (capability + policy evaluation).
3) Effect (explicit, auditable operation).

No direct mutation is allowed outside this pipeline.

## Audit and Explainability
All authority outcomes MUST emit:
- capability grant/deny/override evidence,
- law targets evaluated,
- scope chain used,
- effect identifiers committed.

## Cross-References
- Capability taxonomy: `schema/capabilities/SPEC_CAPABILITY_TAXONOMY.md`
- Negative capabilities: `schema/capabilities/SPEC_NEGATIVE_CAPABILITIES.md`
- Capability scoping: `schema/authority/SPEC_CAPABILITY_DOMAINS.md`
- Law kernel: `schema/law/SPEC_LAW_KERNEL.md`
