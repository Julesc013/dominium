# SPEC_COMMAND_MODEL — Command Intent Model Canon

Status: draft
Version: 1

## Purpose
Define the canonical Command Intent Model: a deterministic, auditable, latency-aware
system by which players and authorities express goals and constraints, and by which
local actors execute them — without direct micromanagement.

This spec is documentation-only. It introduces no runtime logic.

## Core axioms (locked)
1) Commands express intent, not actions.
2) Commands do not directly mutate world state.
3) Commands are delivered via communication (INF2).
4) Commands execute only when delivered.
5) Commands are constrained by local reality and effect fields.
6) Commands may fail, degrade, or abort deterministically.
7) Commands are auditable and replayable.
8) Loss of communication triggers doctrine, not paralysis.
9) Command semantics are identical in SP, MP, and MMO.
10) Removing command authority removes future command effects.

## Definitions

### Command intent
A declarative statement of a goal. Contains:
- intent_id (deterministic)
- issuer (actor/org)
- scope (entity, group, region)
- goal description
- constraints
- priority
- abort conditions
- issue_tick (ACT)

### Command scope
The domain over which a command applies. Examples:
- single entity
- group
- organization
- region
- route
- facility

### Constraints
Hard limits that MUST be respected. Examples:
- budget cap
- risk tolerance
- legal/jurisdictional limits
- time windows

### Abort conditions
Deterministic conditions under which execution stops. Examples:
- resource depletion
- loss of authority
- hazard threshold exceeded
- conflicting higher-priority command

### Command queue
A deterministic, ordered structure that holds pending commands. Ordering rules are
explicit and stable.

## Command lifecycle (mandatory)

ASCII diagram:

  [ Intent Issued ]
          |
          v
  [ Communication (INF2) ]
          |
          v
   [ Delivery Event ]
          |
          v
 [ Enqueue in Local Command Queue ]
          |
          v
    [ Feasibility Check ]
          |
          v
    [ Execution Planning ]
          |
          v
  [ Local Actions (micro/meso) ]
          |
          v
 [ Progress / Completion / Abort ]
          |
          v
      [ Audit Record ]

No step may be skipped.

## Engine vs game responsibilities

Engine (Domino, C89/C90) MAY:
- provide deterministic queues and ordering helpers
- provide canonical identifiers
- provide event scheduling primitives

Engine MUST NOT:
- interpret command meaning
- plan execution
- know about actors or organizations

Game (Dominium, C++98) MUST:
- create CommandIntents
- serialize and transmit them
- maintain command queues
- interpret intent meaning
- generate local actions
- emit audit records

## Execution semantics
- Feasibility checking is performed on delivery and periodically; deterministic.
- Execution planning is local, respects effect fields, and respects resources.
- Partial execution is allowed; progress is persistent.
- Failure modes are deterministic: graceful abort, degradation, escalation.

No teleporting actions. No retroactive execution.

## Priority and conflict resolution
Specify stable ordering rules for priorities and deterministic tie-breaking.
Conflicts must be visible and auditable:
- supersession
- coexistence
- explicit refusal

No hidden resolution.

## Agentless play support (mandatory)
The game must remain playable without AI/NPCs. Commands can be interpreted by
deterministic procedures rather than agent decision-making.

Example:
- "Maintain power grid" translates to a deterministic maintenance procedure
  without AI planning.

## Integration points (mandatory)
- Belief model (INF0): feasibility uses belief constraints
- Communication (INF2): command latency
- Effect fields (EF*): constraints, risk, and degradation
- Refinement/collapse (future)
- Economy commands (future)
- Time windows (future)

## Prohibitions (enforced)
- Direct world mutation by UI
- Per-entity micromanagement APIs
- Instant command execution
- RNG-based planning
- Hidden execution logic

## Worked examples

### Delayed construction command
Issuer sends "build platform" intent. Delivery occurs at arrival_tick. Feasibility
check fails if resources are depleted; abort recorded with reason.

### Aborted logistics command
"Deliver resources" intent executes until a hazard threshold is crossed. Execution
aborts deterministically and escalates to issuer.

### Conflicting orders
Two intents target the same facility. Higher-priority command supersedes; conflict
is recorded and visible in audit.

## References
- Information model: `docs/SPEC_INFORMATION_MODEL.md`
- Communication: `docs/SPEC_COMMUNICATION.md`
- Effect fields: `docs/SPEC_EFFECT_FIELDS.md`

## Test and validation requirements (spec-only)
Implementations must provide:
- deterministic command ordering tests
- latency enforcement tests
- conflict resolution tests
- replay equivalence tests
- lockstep/server-auth parity tests
