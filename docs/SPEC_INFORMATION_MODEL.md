# SPEC_INFORMATION_MODEL — Information & Belief Model Canon

Status: draft
Version: 1

## Purpose
Define the canonical Information & Belief Model: a deterministic epistemic layer
that governs what actors know, how they know it, how knowledge decays, and how
conflicting information coexists — without hiding authoritative reality.

This spec is documentation-only. It introduces no runtime logic.

## Core axioms (locked)
1) There is exactly one authoritative world state.
2) Belief is a projection of world state, never a substitute.
3) Information is produced only by observation or communication.
4) Uncertainty is explicit and bounded.
5) Ignorance is represented as UNKNOWN.
6) Knowledge decays deterministically.
7) Conflicting beliefs are allowed and visible.
8) Belief NEVER affects simulation causality.
9) All belief updates are replayable.
10) Removing an information source removes its contributions.

## Definitions

### Authoritative fact
A true statement about the world state, stored only in engine-level canonical state.

### Information record (InfoRecord)
A derived datum produced by observation or communication. Contains:
- subject (entity, location, contract, time)
- observed value or interval
- resolution tier
- uncertainty envelope
- source
- ACT timestamp
- decay parameters

### Belief store
A deterministic collection of InfoRecords for an actor. Supports:
- merge
- decay
- conflict coexistence
Never stores authoritative facts.

### Resolution tiers
At minimum:
- UNKNOWN
- BINARY (exists / not)
- COARSE (order-of-magnitude)
- BOUNDED (min/max interval)
- EXACT (rare, expensive)

### Decay
A deterministic widening of uncertainty over ACT. Decay may:
- widen bounds
- downgrade resolution tier
- mark info as stale

Decay NEVER introduces randomness.

## Belief update pipeline (mandatory)

ASCII diagram:

  [ Authoritative World State ]
              |
              v
      [ Sensors / Observers ]
              |
              v
  [ Effect Fields (Perception) ]
              |
              v
     [ Communication Channels ]
              |
              v
       [ InfoRecord Creation ]
              |
              v
  [ Belief Store Merge + Decay ]

At no point does belief modify world state.

## Engine vs game responsibilities

Engine (Domino, C89/C90) MAY:
- provide hooks to read authoritative state
- tag facts with canonical identifiers
- provide deterministic math for decay envelopes

Engine MUST NOT:
- store beliefs
- resolve conflicts
- know about actors' knowledge

Game (Dominium, C++98) MUST:
- store BeliefStores per actor/faction
- manage InfoRecords
- apply decay rules
- resolve display of conflicts
- integrate with UI and commands

## Fog-of-war semantics
Fog-of-war is NOT hiding entities. It is:
- lack of InfoRecords
- low resolution InfoRecords
- stale InfoRecords

Actors may:
- know an entity exists but not where
- know approximate values but not exact
- hold mutually inconsistent reports

## Conflict handling (mandatory)
- Multiple InfoRecords about the same subject coexist.
- Conflicts are presented, not auto-resolved.
- Confidence and source provenance are shown.
- Newer info does NOT necessarily invalidate older info.

No silent resolution. No "truth picking."

## Domains that must use belief model
- Maps and geography
- Time and calendars
- Economy (prices, balances)
- Governance and law
- Military and security
- Construction and infrastructure
- Population and demography
- Science and research
- Death and continuity events

## Integration points

### Effect fields
Perception filters are effect fields that influence InfoRecord creation but never
modify authoritative reality. See `docs/SPEC_EFFECT_FIELDS.md`.

### Communication
Comms channels transform InfoRecords deterministically and may degrade resolution
tiers or add latency. No RNG. No hidden synthesis.

### Epistemic UI
UI must show uncertainty and conflicts explicitly and must not query authoritative
world state directly. See `docs/SPEC_EPISTEMIC_GATING.md`.

### Command intent
Commands may specify intent using belief data, but authoritative validation uses
canonical state. Mismatch must be surfaced as refusal or conflict.

## Prohibitions (enforced)
- Random fog
- Binary "seen/unseen" toggles
- UI querying world state directly
- Clearing belief on reload
- Non-deterministic decay
- Auto-merging conflicting info

## Worked examples

### Conflicting reports
Two sensors report different resource yields for the same site. Both InfoRecords
remain in the BeliefStore, marked by source and confidence. UI displays the
conflict rather than choosing one.

### Stale vs fresh info
An old report gives an EXACT location. As ACT advances, the uncertainty envelope
widened and the resolution tier degrades to BOUNDED. A newer COARSE report does
not delete the old one; both are retained.

### Map uncertainty
An actor knows an entity exists (BINARY) but has no position InfoRecord. The map
shows a "known to exist" marker without coordinates.

### Time disagreement
Two jurisdictions publish different calendars for the same interval. Both are
rendered with conflict markers; canonical ACT remains the source of truth.

## Test and validation requirements (spec-only)
Implementations must provide:
- deterministic decay tests
- merge consistency tests
- conflict persistence tests
- replay equivalence tests
- lockstep vs server-auth parity tests
