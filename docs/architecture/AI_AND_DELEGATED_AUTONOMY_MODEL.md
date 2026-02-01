Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# AI and Delegated Autonomy Model (AIA0)

Status: binding.  
Scope: AI-native agents, delegation contracts, and deterministic planning.

## Core invariant
**AI agents differ from human players only in how they choose actions — never in
what actions they are allowed to perform.**

AI is not:
- omniscient
- perfectly rational
- exempt from law
- immune to error
- outside replay

## Authoritative primitives
AI autonomy is represented through three data primitives:
- **Goals** (`schema/agent.goal.schema`)
- **Delegations** (`schema/agent.delegation.schema`)
- **Autonomy budgets** (`schema/agent.autonomy_budget.schema`)

All numeric values are fixed-point in authoritative logic and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## Process-only mutation
AI state changes only through Processes. Canonical process families (data-defined) include:
- `org.dominium.process.autonomy.plan`
- `org.dominium.process.autonomy.execute`
- `org.dominium.process.autonomy.revise`
- `org.dominium.process.autonomy.revoke`

No hidden planning loops or per-tick global AI updates are allowed.

## Deterministic planning
Planning is a bounded, deterministic search over existing processes and jobs:
- search order is stable and deterministic
- budgets bound depth, branching, and compute cost
- named RNG streams only (if stochastic choice is permitted by law)
- every decision is explainable and replayable

Planning MAY fail or return suboptimal plans.

## Delegation and oversight
Delegation contracts define:
- allowed process families
- budget limits (time, energy, risk)
- oversight policies (pause, approve, revoke)
- revocation conditions

Refusals must follow `docs/architecture/REFUSAL_SEMANTICS.md`.

## Knowledge and skill limits
AI is constrained by:
- available knowledge artifacts (T18)
- skill profiles and variance limits
- outdated or incorrect information
- communication latency and uncertainty (T14)

No perfect foresight or privileged sensing is allowed.

## Institutional AI
Institutions can operate AI agents as administrators, inspectors, or regulators:
- legitimacy and compliance constraints apply (T17/T19)
- capacity limits and budget exhaustion apply
- paperwork and audit artifacts are produced

Institutional AI can be incompetent or corrupt; outcomes are not guaranteed.

## Collapse/expand compatibility
Macro capsules store:
- active delegated goals per domain (invariant)
- plan success/failure distributions
- autonomy budget utilization statistics
- RNG cursor continuity (if used)

Expanded domains reconstruct deterministic microstates consistent with capsules.

## Save/load/replay
- Goals, delegations, and autonomy budgets are saved as authoritative data.
- Plans and revisions are saved as process events.
- Replays reproduce identical decisions and failures.

## Non-goals (AIA0)
- No nondeterministic ML inference.
- No AI-only capabilities or god-mode planners.
- No global omniscient scheduling.

## See also
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`
- `docs/architecture/RNG_MODEL.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`
- `docs/architecture/UNIT_SYSTEM_POLICY.md`