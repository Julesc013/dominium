--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Knowledge item rules, research output handling, and epistemic status.
SCHEMA:
- Knowledge item record format and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No floating point fields in authoritative knowledge.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_KNOWLEDGE_ITEMS - Knowledge Items (CIV3)

Status: draft  
Version: 1

## Purpose
Define deterministic knowledge items and epistemic status for CIV3.

## KnowledgeItem schema
Required fields:
- knowledge_id
- type (theory/method/design/doctrine)
- domain_tags (bitset or canonical tag ids)
- completeness (0..1000 fixed-point, integer)
- provenance_ref
- epistemic_status (unknown/rumored/known)

Rules:
- completeness MUST use integer fixed-point (no floats).
- epistemic_status MUST reflect knowledge access, not global truth.

## Determinism requirements
- Knowledge IDs are stable and ordered.
- Updates to completeness are deterministic and ACT-driven.
- No global scans of all knowledge items.

## Integration points
- Research processes: `schema/knowledge/SPEC_RESEARCH_PROCESSES.md`
- Diffusion: `schema/knowledge/SPEC_DIFFUSION.md`
- Epistemic interface: `docs/SPEC_EPISTEMIC_INTERFACE.md`

## Prohibitions
- No omniscient knowledge exposure in UI.
- No random or wall-clock derived knowledge updates.
