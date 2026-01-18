--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Research scheduling, prerequisite checks, and output handling.
SCHEMA:
- Research process record format and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No per-tick research scanning.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_RESEARCH_PROCESSES - Event-Driven Research (CIV3)

Status: draft  
Version: 1

## Purpose
Define deterministic research processes that schedule start and completion
events instead of per-tick updates.

## ResearchProcess schema
Required fields:
- process_id
- institution_id
- start_act
- completion_act
- prerequisites (knowledge_id + min_completeness)
- output_knowledge_ids
- next_due_tick
- status (pending/active/completed/refused)

Rules:
- start_act and completion_act are ACT times.
- prerequisites MUST be met before activation.
- outputs MUST reference pre-declared KnowledgeItem IDs.

## Determinism requirements
- Research ordering is stable (process_id tie-breaks).
- Batch vs step equivalence MUST hold.
- No global iteration over all research processes.

## Integration points
- Knowledge items: `schema/knowledge/SPEC_KNOWLEDGE_ITEMS.md`
- Diffusion: `schema/knowledge/SPEC_DIFFUSION.md`
- Institutions: `schema/knowledge/SPEC_SECRECY.md`

## Prohibitions
- No continuous per-frame research ticking.
- No research completion based on wall-clock time.
