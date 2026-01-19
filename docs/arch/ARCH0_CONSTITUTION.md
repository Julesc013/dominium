# ARCH0 Constitution

Status: binding, non-negotiable.
Scope: architecture, simulation law, data boundaries, and enforcement.
If any document, code, data, or prompt conflicts with ARCH0, ARCH0 wins.

## Purpose
ARCH0 defines the architectural invariants, the mental model, and the change
protocol that govern all present and future development. It is not a style
guide. It is the constitution of the project.

## Core Axioms (Absolute)
A1. Determinism is the primary invariant.
- Authoritative simulation must be deterministic.
- Batch vs step equivalence is mandatory.
- Non-determinism is allowed only in presentation, advisory systems, or
  explicitly marked derived layers.

A2. Simulation advances only via events.
- No per-tick global scans.
- No implicit background simulation.
- All progression must be scheduled or amortized.

A3. Provenance is mandatory.
- Nothing may exist without a causal chain.
- Creation, mutation, transfer, and destruction must be auditable.

A4. Laws govern existence and action.
- Meta-law (existence), capability law (who), policy law (how) apply everywhere.
- No bypasses, no hard-coded exceptions.

Law enforcement points and law kernel schemas are defined in:
- `docs/arch/LAW_ENFORCEMENT_POINTS.md`
- `schema/law/README.md`

A5. Engine and game are strictly separated.
- Engine defines mechanisms.
- Game defines meaning.
- Data defines configuration.
- Tools observe, never mutate.

A6. Everything degrades gracefully.
- Every system declares fidelity tiers.
- Every system declares a degradation ladder.
- Budgets are hard limits, not suggestions.

A7. Absence must be valid.
- Systems may be disabled entirely.
- Zero agents, zero AI, zero economy, zero war must still function.

## System Model (Mandatory)
All systems must be expressible as:

1. Intent
   - A request to do something.
2. Action
   - A law-validated operation.
3. Effect
   - Scheduled consequences with irreversibility classification.

Each layer must be interceptable by:
- Law kernel
- Governance
- Tooling (read-only)
- Explanation system

## Execution Substrate (EXEC0)
All authoritative work MUST be expressed as Work IR with Access IR declarations,
as defined in `schema/execution/README.md`. EXEC0 is binding and subordinate to
ARCH0.

Deterministic reordering, reduction, and commit ordering are governed by:
- `docs/arch/EXECUTION_REORDERING_POLICY.md`
- `docs/arch/DETERMINISTIC_REDUCTION_RULES.md`

## ECS Component Schema (ECSX0)
Component meaning and field semantics are defined by ECSX0 schema docs under
`schema/ecs/README.md`. Physical storage layout is a backend choice and must
not alter logical meaning or determinism guarantees.

## Irreversibility Framework
Every sim-affecting effect must declare one of:
- REVERSIBLE (UI, planning, advisory only)
- COMPENSABLE (can be countered by a new effect, not undone)
- IRREVERSIBLE (death, knowledge diffusion, cultural change)

Effects without classification are invalid.

## Module Discipline
Modules must declare:
- Category: foundational, compositional, derived, decorative
- Dependencies (explicit)
- Invariants preserved
- Invariants consumed

Circular dependencies are forbidden. Undeclared semantics are forbidden.

## Data vs Code Boundary
MUST BE CODE:
- Execution semantics
- Scheduling rules
- Law resolution algorithm
- Determinism enforcement
- ECS storage mechanics

MUST BE DATA:
- Laws and policies
- Capabilities and sets
- Module activation
- Gameplay styles
- World content
- Standards (time, currency, units)

## No Silent Fallback Rule
Fallbacks must be explicit, deterministic, auditable, and visible to tooling.
Silent fallback is architectural failure.

## Counterfactual Rule
Authoritative simulation must never branch, speculate, or rollback for "what if".
Counterfactuals must run in explicit shadow instances, non-authoritative
sandboxes, or budgeted environments.

## Advisory AI Rule
AI systems may explain, summarize, propose, and translate. AI systems may not
decide outcomes, mutate authoritative state, or bypass law/capability gates.

## Change Protocol (Mandatory)
Any change that affects determinism, authoritative state, schema meaning, law
semantics, or execution model requires the change protocol in
`docs/arch/CHANGE_PROTOCOL.md`. Unreviewed architectural drift is forbidden.

## Enforcement
ARCH0 must be referenced by all future prompts, enforced by CI checks, and
required reading for contributors. Violations result in refusal, not workaround.

## Glossary
See `docs/arch/GLOSSARY.md` for binding definitions.
