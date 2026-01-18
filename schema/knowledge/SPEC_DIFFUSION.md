--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Diffusion scheduling, delivery ordering, and epistemic gating.
SCHEMA:
- Diffusion event record format and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No global knowledge broadcast.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_DIFFUSION - Knowledge Diffusion Events (CIV3)

Status: draft  
Version: 1

## Purpose
Define deterministic knowledge diffusion via scheduled events.

## DiffusionEvent schema
Required fields:
- diffusion_id
- knowledge_id
- src_actor_id
- dst_actor_id
- channel_id (INF2)
- send_act
- receive_act
- fidelity (integer bucket or fixed-point)
- uncertainty (integer bucket or fixed-point)
- secrecy_policy_id
- next_due_tick
- status (pending/delivered/blocked)

Rules:
- Delivery occurs at receive_act only.
- Ordering uses (receive_act, diffusion_id).
- Knowledge only propagates through explicit diffusion events.

## Determinism requirements
- Diffusion scheduling is stable and replayable.
- Batch vs step equivalence MUST hold.
- No random or wall-clock delivery.

## Integration points
- Secrecy policies: `schema/knowledge/SPEC_SECRECY.md`
- Info/comm systems: `docs/SPEC_COMMUNICATION.md`

## Prohibitions
- No implicit global knowledge unlocks.
- No UI access to authoritative knowledge without diffusion.
