Status: AUTHORITATIVE
Last Reviewed: 2026-02-16
Version: 1.0.0
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Factions and Affiliation

## Scope
This document defines the CIV-1 structural substrate for faction state, subject affiliation, and ownership-safe multiplayer behavior.

## Canonical Model
- `Faction` is a Truth-side assembly (`assembly.faction.*`) created and mutated only by deterministic processes.
- `Affiliation` is a field-level relation on subjects (`agent_id` and future cohort/population IDs).
- `Territory` is modeled as a region-level assembly with owner and claim status.
- `Diplomacy` is represented as structured relation state with no gameplay semantics in CIV-1.

## Non-Goals in CIV-1
- No implicit player faction.
- No inventory/crafting/combat/economy solvers.
- No war/trade gameplay effects.
- No mode flags.

## Determinism and Mutation Invariants
- All authoritative mutation routes through process handlers.
- IDs are stable and deterministic.
- Conflict ordering is deterministic and explicitly sorted.
- Zero-agent and single-agent worlds remain valid.

## Multiplayer Authority
- Faction, affiliation, territory, and diplomacy state are authoritative server-side in replicated sessions.
- Lockstep carries civ intents as deterministic process intents.
- Server-authoritative and hybrid routes must apply authority checks before mutation.
