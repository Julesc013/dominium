# AGENT2 — Doctrine, Roles, and Delegation

Status: draft
Version: 1

## Purpose
Define doctrine-driven autonomy for agents without introducing new mechanics.
Doctrine constrains goal selection and scheduling while agents remain command
issuers only.

## Scope (AGENT2)
- Doctrine filtering and priority modification.
- Role binding and requirements.
- Delegation authority enforcement.
- Event-driven doctrine updates.
- Cohort-level autonomy collapse.

## Canonical modules
- `game/agents/doctrine.*`
- `game/agents/agent_role.*`
- `game/agents/delegation.*`
- `game/agents/doctrine_scheduler.*`

Public headers live in `game/include/dominium/agents/`.

## Determinism rules
- Doctrine selection order is explicit and stable.
- Priority modifiers are fixed-point and bounded.
- Doctrine updates are scheduled events only.
- Batch vs step equivalence must hold.

## Doctrine resolution order
1) explicit context
2) role doctrine
3) org doctrine
4) jurisdiction doctrine
5) personal fallback
6) refusal

## Delegation rules
- Explicit delegation only; no implicit authority.
- Expired delegations refuse command attempts.

## Cohort autonomy
- Cohort planners collapse multiple agents into a single plan deterministically.
- Refinement restores individual agents deterministically.

## Tests (AGENT2)
Implemented in `game/tests/agent2_doctrine_tests.cpp`:
- Doctrine filtering determinism.
- Priority modification determinism.
- Conflicting doctrine resolution.
- Cohort-level autonomy collapse.
- Batch vs step equivalence for doctrine updates.
- No doctrine -> no autonomous actions.
