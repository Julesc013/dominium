--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- None. Game consumes engine primitives where applicable.

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
# SPEC_STANDARDS_AND_RENDERERS — Standards, Ledgers, and Renderers Canon

Status: draft
Version: 1

## Purpose
Define a single, reusable abstraction for human-invented standards that can be applied
to time, currency, units, law, communications, governance, naming, mapping, and more.
This framework must be deterministic, data-driven, and safe across all scales.

This spec is authoritative for intent, definitions, constraints, and invariants.
It introduces no runtime logic; it constrains future implementation.

## Core axioms (locked)
1) Authoritative reality is stored ONLY in canonical quantities.
2) Standards NEVER create, destroy, or modify reality.
3) Standards are renderers + policies over canonical quantities.
4) All standards are stateless.
5) All conversions are deterministic.
6) Conflicts between standards are EXPECTED and gameplay-relevant.
7) Unknown information is represented as UNKNOWN, never guessed.
8) Aggregation is compression, never fabrication.
9) Everything must round-trip deterministically.
10) Engine code must NEVER reference named real-world standards.

## Definitions

### Authoritative quantity
A value stored in canonical units in the engine. It is the only form of authoritative
reality and is always representable without a standard.

Examples:
- time -> ACT seconds (canonical), or tick_index + ups as authoritative timebase
- length -> canonical meters (fixed-point)
- mass -> canonical kilograms (fixed-point)
- energy -> canonical joules (fixed-point)
- value -> base asset units (integer or fixed-point)

### Standard
A data-defined object that describes how to render an authoritative quantity and how
to apply policies over it (labeling, rounding, localization, conflict rules).
Standards are stateless and never mutate authoritative quantities.

Examples of standards:
- calendar
- currency
- unit system
- fiscal year definition
- legal code presentation
- market structure conventions

### Renderer
A pure function:

    (authoritative quantity + parameters) -> representation

Renderers must be deterministic and reversible where mathematically possible.
They never store state and must not access wall-clock time or external sources.

### Ledger
A deterministic state machine that enforces conservation and explicit obligations.
Ledgers are used for economy, assets, contracts, and obligations. They operate only
on canonical quantities and are independent of standards and renderers.

### Standard resolution context
The situation in which a standard is chosen. It includes explicit documents, actor
knowledge, organization membership, jurisdiction, device availability, and runtime
policy. Resolution order is defined in `docs/SPEC_STANDARD_RESOLUTION.md`.

### Epistemic gating
A standard or renderer is usable only if the actor knows it and has required access
or authority. Lack of knowledge produces UNKNOWN, not defaults.

## Engine vs game responsibilities

Engine (Domino, C89/C90) MAY:
- store authoritative quantities
- perform canonical math
- advance time
- execute ledgers and contracts
- schedule deterministic events

Engine MUST NOT:
- know about calendars
- know about currencies
- know about unit names
- know about locales
- know about jurisdictions
- format values for UI

Game (Dominium, C++98) MAY:
- load standards from data packs
- resolve standards by context
- render quantities for UI
- apply epistemic gating
- display uncertainty and conflict

## Relationships and flow

ASCII diagram:

  [Authoritative Quantity] -----> [Renderer(Standard)] -----> [Representation]
            |
            v
         [Ledger]
     (conservation, obligations)

Standards never touch ledgers or canonical quantities. Ledgers never depend on
standards for math or policy.

## Determinism and round-trip guarantees
- Rendering a quantity and parsing it back (when reversible) must yield the same
  canonical value within defined rounding rules.
- All conversions must be deterministic across platforms and runs.
- No random rounding, no locale-dependent defaulting, no silent fallbacks.

## Conflict visibility
Conflicts are part of gameplay and must be visible. If standards conflict:
- the conflict is surfaced (UI, logs, or documents)
- resolution is explicit and auditable
- UNKNOWN is used where resolution is not possible

## Prohibitions (engine and tooling)
The following are forbidden as hard-coded identifiers or logic in engine code:
- "Gregorian"
- "UTC"
- "USD"
- "meters"
- "ISO"

These labels may appear only as data-defined standards in content packs.
Engine code must not branch on, parse, or format based on those names.

## Non-examples (what NOT to do)
- "If locale == en_US then format time as Gregorian" (engine-side, forbidden)
- "If currency == USD then round to cents" (UI-side policy without standard data)
- "Assume meters as display unit by default" (silent fallback)
- "If no standard found, choose a default without reporting conflict" (forbidden)
- "Use wall-clock time to resolve a calendar" (non-deterministic)

## Worked examples (cross-domain)

### Time
Authoritative time is stored as tick_index + ups (or ACT seconds).
Renderer standards (data-defined) may include:
- HPC-E calendar
- Gregorian-like calendar
- SCT calendar

Conflict example:
Two parties sign a contract in a mixed jurisdiction. The contract specifies HPC-E
for deadlines; a UI override requests SCT for display. The resolution order yields
HPC-E as authoritative display in the contract view, while SCT is permitted only
as a secondary, conflict-marked view.

### Currency
Authoritative value is stored as base asset units in a ledger.
Renderer standards provide currency labels and rounding policy.

Conflict example:
A trade uses a local currency standard, but the organization accounting uses a
different currency standard. Both renderings must be shown with explicit conflict
flags. The ledger remains unchanged in base asset units.

### Units
Authoritative distance is stored in canonical meters (fixed-point).
Renderer standards provide SI-like or Imperial-like unit systems as data.

Device failure example:
An actor loses access to a measurement device, so unit standards are not usable.
The system renders UNKNOWN rather than silently defaulting to any unit system.

### Governance
Authoritative facts are stored in canonical quantities and ledger states.
Jurisdiction standards provide legal labels and interpretations for UI and docs.

Misunderstanding example:
Player reads a rule under their personal standard, but the jurisdiction standard
differs. The UI must show a conflict warning and the authoritative standard used
for that document.

## Future domain references (non-exhaustive)
- calendars and time standards (see `docs/SPEC_CALENDARS.md`)
- currencies and economy (see `docs/SPEC_ECONOMY.md`)
- unit systems (see `docs/SPEC_NUMERIC.md` for canonical storage constraints)
- legal and governance standards (future specs)
- comms and identity naming (see `docs/SPEC_KNOWLEDGE.md`)

## Test and validation requirements (spec-only)
Implementations must provide:
- round-trip tests (quantity -> renderer -> quantity)
- conflict visibility tests
- UNKNOWN propagation tests
- determinism tests across platforms
- validation rules that reject hard-coded defaults and non-deterministic policies
