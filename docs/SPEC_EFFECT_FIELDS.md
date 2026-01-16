--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

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
# SPEC_EFFECT_FIELDS — Effect Field Canon (Rates, Constraints, Perception)

Status: draft
Version: 1

## Purpose
Define the canonical Effect Field abstraction: a deterministic, composable mechanism
that modifies rates, constraints, asymmetries, irreversibility, and perception without
modifying authoritative clocks, geometry, or state ownership.

This spec is documentation-only. It introduces no runtime logic.

## Core axioms (locked)
1) Effect fields NEVER change authoritative time.
2) Effect fields NEVER change authoritative geometry.
3) Effect fields NEVER change ownership or provenance.
4) Effect fields ONLY modify:
   - rates
   - constraints
   - asymmetries
   - irreversibility
   - perception
5) Effect fields are deterministic functions.
6) Effect fields are composable in a fixed order.
7) Effect fields are data-defined.
8) Effect fields apply uniformly across all subsystems.
9) Unknown effects propagate as UNKNOWN, not guessed.
10) Removal of an effect source removes the effect.

## Definitions

### Effect field
A pure, deterministic function:

    Effect = f(Context, ACT)

It produces no side effects and stores no state.

### Effect context
Immutable inputs including:
- domain (cosmo/system/site/local)
- subject (entity, location, route)
- environment (biome, medium)
- active standards
- active governance
- ACT timestamp

### Effect output
A structured set of modifiers:

Rate modifiers:
- multiplicative or additive scalars
- examples: production_rate, decay_rate, event_frequency, learning_rate

Constraint flags:
- boolean or enum
- examples: docking_forbidden, construction_disallowed, measurement_requires_device

Asymmetries:
- directional or contextual penalties
- examples: inbound_vs_outbound_navigation, information_send_vs_receive

Irreversibility flags:
- mark transitions as one-way
- examples: no_return_zone, measurement_locks_state

Perception filters:
- affect epistemic systems
- examples: sensor_blur, latency_multiplier, confidence_widening

Resolution cost modifiers:
- cost to refine uncertainty
- examples: survey_cost, calibration_cost

## Composition order (mandatory)
1) System-level effect fields
2) Region-level effect fields
3) Site-level effect fields
4) Local/transient effect fields

Rules:
- Order is fixed and documented.
- Later layers may refine but not negate higher layers.
- Composition is deterministic.
- Composition is associative only in defined ways.

ASCII diagram:

  Context -> System -> Region -> Site -> Local -> Final Effect

## Engine vs game responsibilities

Engine (Domino, C89/C90) MAY:
- define effect output structures
- perform pure effect evaluation
- compose effect outputs
- hash sim-affecting components

Engine MUST NOT:
- interpret meaning
- know about calendars or currencies
- access UI or devices

Game (Dominium, C++98) MAY:
- bind effect fields to content
- define effect field sources in data packs
- map effects to gameplay interpretation
- display effect consequences via UI

## Relativistic-like effects (modeled)
Effect fields model "relativistic-like" behavior without changing ACT:
- time dilation -> rate compression, accelerated decay, shortened decision windows
- event horizon -> irreversibility flags, no_return constraints, information loss
- frame asymmetry -> directional penalties, planning uncertainty

No physics equations. No spacetime curvature. No local timebases.

## Quantum-like effects (modeled)
Effect fields model "quantum-like" behavior without RNG:
- superposition -> latent state sets
- measurement -> deterministic collapse
- uncertainty -> bounded envelopes
- entanglement -> state coupling constraints

No probabilities. No RNG. No wavefunctions.

## Domains that must use effect fields
Effect fields must be the universal modifier system for:
- movement and navigation
- construction and engineering
- atmospheres and media
- economy and markets
- information and sensors
- communication and latency
- governance and law
- risk and insurance
- time warp gating
- death and continuation policies

## Integration points

### World Source Stack (WSS)
Effect fields consume WSS outputs but never replace them. WSS provides authoritative
environmental inputs; effect fields provide modifiers and constraints.

### Fidelity projection
Effect outputs are projected into presentation fidelity layers. Reduced fidelity is
allowed but must not alter authoritative quantities.

### Epistemic UI
Effect outputs can gate or degrade perception. Unknown effects propagate as UNKNOWN.
See `docs/SPEC_EPISTEMIC_GATING.md`.

### Time warp
Effect fields can gate or constrain warp by altering rates and constraints; they do
not change ACT or tick progression rules.

## Prohibitions (enforced)
- Per-region tick rates
- Local clocks
- Floating-point chaos
- RNG-based effects
- Hard-coded zones
- Domain-specific effect hacks

## Positive examples

### Environmental hazard
System-level radiation field sets:
- decay_rate multiplier > 1
- survey_cost multiplier > 1

Region-level effect refines with directional penalties for inbound travel.

### Governance constraint
Site-level effect sets:
- construction_disallowed = true
- measurement_requires_device = true

Local transient effect adds latency_multiplier for sensors.

### Economic pressure
System effect sets:
- production_rate multiplier < 1
- interest_rate additive modifier > 0

No ledger changes occur here; only modifiers for gameplay interpretation.

## Negative examples (forbidden)
- "Local clock runs slower in a nebula."
- "Use RNG to jitter event outcomes."
- "Apply a special-case physics solver for a zone."
- "Change geometry to reflect a field."
- "If no effect data exists, assume safe."

## Test and validation requirements (spec-only)
Implementations must provide:
- determinism tests for effect evaluation
- composition order tests
- removal tests (source gone -> effect gone)
- sim-hash boundary tests (sim-affecting vs non-sim fields)
- cross-domain consistency tests
