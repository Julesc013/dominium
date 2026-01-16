--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC_DOCTRINE_AUTONOMY — Doctrine & Autonomy Canon

Status: draft
Version: 1

## Purpose
Define the canonical Doctrine & Autonomy system: a deterministic, rule-driven
execution layer that interprets Command Intents locally when communication is
delayed, disrupted, or intentionally abstracted.

This spec is documentation-only. It introduces no runtime logic.

## Core axioms (locked)
1) Autonomy is rule-based, not agent-based.
2) Doctrine interprets intent; it does not invent goals.
3) Doctrine is deterministic and auditable.
4) Doctrine never bypasses constraints or provenance.
5) Doctrine never executes outside its authority.
6) Doctrine respects effect fields and fog-of-war.
7) Loss of comms activates doctrine, not paralysis.
8) Autonomy is identical in SP, MP, and MMO.
9) Removing doctrine removes autonomous behavior.
10) Doctrine evaluation cost is bounded.

## Definitions

### Doctrine
A deterministic set of rules governing local behavior. Bound to:
- an entity
- a facility
- a group
- an organization

Contains:
- trigger conditions
- permitted actions
- thresholds
- priorities
- fallback behaviors

### Doctrine rule
A single rule of the form:

    IF (conditions) THEN (actions) WITH (constraints)

### Conditions
Deterministic predicates over:
- local state
- delivered commands
- belief state (INF0)
- effect fields (EF*)
- time windows

### Actions
Deterministic, local actions that:
- enqueue jobs
- adjust rates
- request resources
- send reports
- issue subordinate commands

### Fallback behavior
Explicit behavior used when:
- no commands are present
- comms are lost
- constraints block execution

## Doctrine evaluation model (mandatory)
Doctrine is evaluated:
- on delivery of new commands
- on significant local state change
- on scheduled review ticks

Evaluation is:
- ordered
- bounded
- deterministic

No doctrine is evaluated every tick by default.

ASCII diagram:

  [ Command Delivery ]      [ Local State Change ]      [ Review Tick ]
           |                        |                       |
           +-------------> [ Doctrine Evaluation ] <--------+
                                   |
                                   v
                            [ Local Actions ]

## Engine vs game responsibilities

Engine (Domino, C89/C90) MAY:
- provide deterministic evaluation helpers
- provide canonical ordering primitives
- provide event scheduling support

Engine MUST NOT:
- contain doctrine rules
- interpret doctrine meaning
- access belief or UI

Game (Dominium, C++98) MUST:
- define doctrine schemas
- evaluate doctrine rules
- enqueue local actions
- emit audit records
- expose doctrine editing tools

## Supported doctrine scopes
Doctrine must be applicable to:
- individual body (e.g. "keep me alive")
- facility (factory operation)
- infrastructure (power grid)
- logistics route
- city/settlement
- organization (corporation, government)
- military unit (defensive posture)

Each scope must have explicit authority limits and explicit fallback behaviors.

## Conflict and priority handling
Doctrine interacts with Command Intents as follows:
- Command Intents define goals and constraints.
- Doctrine chooses local actions within those constraints.
- Conflicts are explicit and auditable.

Priority rules must be explicit, stable, and deterministic:
- doctrine rules have stable ordering
- command priority supersedes doctrine priority unless explicitly delegated
- multiple doctrines compose via ordered precedence (e.g., facility then org)

## Agentless play (mandatory)
Doctrine replaces per-agent "brains." Examples:
- A player issues "maintain power grid."
- Doctrine executes deterministic maintenance procedures without AI planning.
- The same system scales from single facilities to civilization-wide management.

## Worked examples (mandatory)

### 1) Factory doctrine
Rule:
IF input_stock < threshold THEN reduce output_rate
WITH constraints: budget_cap, safety_limits

Fallback:
If no commands and inputs exhausted, enter idle-safe mode.

### 2) City doctrine
Rule:
IF power_supply < minimum THEN ration non-critical zones
WITH constraints: legal limits, public safety thresholds

Fallback:
If comms lost, use emergency ration policy.

### 3) Logistics doctrine
Rule:
IF hazard_level > tolerance THEN reroute via safe path
WITH constraints: time_window, capacity limits

Fallback:
If no route available, suspend transfers and report.

### 4) Military doctrine
Rule:
IF casualties > X THEN fall back to defensive posture
WITH constraints: jurisdictional limits, ROE profile

Fallback:
If comms lost, hold position.

### 5) Household doctrine
Rule:
IF food_supply < threshold THEN prioritize essentials
WITH constraints: budget, health requirements

Fallback:
If no directives, maintain minimum survival policy.

## Prohibitions (enforced)
- AI planners
- random decision-making
- per-entity thinking loops
- implicit or hidden goals
- undocumented heuristics

## Integration references
- Command intent: `docs/SPEC_COMMAND_MODEL.md`
- Information model: `docs/SPEC_INFORMATION_MODEL.md`
- Effect fields: `docs/SPEC_EFFECT_FIELDS.md`
- Fidelity projection (see `docs/SPEC_FIDELITY_DEGRADATION.md`; projection spec TBD)

## Test and validation requirements (spec-only)
Implementations must provide:
- deterministic doctrine evaluation tests
- bounded cost tests
- conflict resolution tests
- doctrine removal tests
- replay equivalence tests
