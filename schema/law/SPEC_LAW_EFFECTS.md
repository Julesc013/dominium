# SPEC_LAW_EFFECTS (EXEC0c)

Schema ID: LAW_EFFECTS
Schema Version: 1.0.0
Status: binding.
Scope: law evaluation outcomes and effects.

## Purpose
Define legal law outcomes and their deterministic payloads.

## LawDecision
Each evaluation returns exactly one of:
- ACCEPT
- REFUSE
- TRANSFORM
- CONSTRAIN

All outcomes MUST be deterministic and auditable.

## REFUSE
Fields:
- refusal_code (stable token)
- violated_law_refs (ordered list)
- precedence_chain (ordered list of scopes applied)
- explanation_meta (deterministic metadata)
- visibility_class (who may see the explanation)

## TRANSFORM
Fields:
- transforms (ordered list of deterministic transforms)
- violated_law_refs (optional)
- precedence_chain
- explanation_meta
- visibility_class

Allowed transforms:
- Fidelity transform: micro -> meso -> macro -> latent
- Cadence transform: increase next_due_tick spacing
- Parameter transform: clamp rates or quotas
- Replace-by-module: swap to an allowed alternate module

Forbidden transforms:
- Changing determinism_class of an authoritative task
- Injecting new side effects
- Altering authoritative history

## CONSTRAIN
Fields:
- constraints (ordered list)
- precedence_chain
- explanation_meta
- visibility_class

Constraint examples:
- quota caps
- time windows
- rate limits

Constraints must be deterministic and auditable.

## ACCEPT
Fields:
- precedence_chain
- explanation_meta (optional)
- visibility_class (optional)

## Fixed Audit Requirements
Every REFUSE, TRANSFORM, or CONSTRAIN MUST record:
- refusal or transform code (if applicable)
- law references consulted
- precedence chain
- visibility classification
