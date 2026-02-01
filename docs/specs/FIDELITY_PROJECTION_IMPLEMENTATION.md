Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Fidelity Projection Implementation (SCALE2)

This document defines the enforceable skeleton for fidelity projection.
It is law. All fidelity transitions MUST pass through the interfaces in `game/include/dominium/fidelity.h`.

## Non-Negotiable Rules

- Fidelity transitions MUST be explicit, deterministic, and provenance-preserving.
- Refinement and collapse MUST be inverse operations and MUST NOT change counts, inventory, or obligations.
- Visible or pinned entities MUST NOT collapse below `DOM_FIDELITY_MICRO`.
- Interest Sets are the ONLY driver for refinement; camera/UI state MUST NOT activate simulation.
- Approximation, LOD shortcuts, and ad-hoc spawn/despawn are FORBIDDEN in authoritative code.

## Canonical Fidelity Model

Authoritative fidelity state is represented by:

- `dom_fidelity_tier` (`LATENT`, `MACRO`, `MESO`, `MICRO`, `FOCUS`)
- `dom_fidelity_state` (tier, last transition tick, pin flags, provenance hash)
- `dom_fidelity_object` (identity + counts/inventory/obligations)

Implementation lives in `game/include/dominium/fidelity.h` and `game/core/dom_fidelity.c`.

## Transition Lifecycle

Transitions MUST be requested and applied deterministically.

```text
request_refine/collapse()
    ↓ (queued, deterministic order)
apply_requests() @ ACT boundary
    ↓ (policy + interest gating + provenance check)
transition applied or refused
```

Rules:

- Requests MUST be queued and sorted deterministically.
- Apply MUST be called at safe ACT boundaries only.
- Refusals are REQUIRED when provenance or pinning would be violated.

## Allowed Transition Graph

Transitions are allowed only between adjacent tiers:

```text
LATENT ↔ MACRO ↔ MESO ↔ MICRO ↔ FOCUS
```

Direct jumps across multiple tiers are FORBIDDEN unless explicitly approved in governance.

## Interest Gating

- Refinement MUST require interest strength >= `refine_min_strength`.
- Collapse MUST require interest strength <= `collapse_max_strength`.
- Interest strength is computed via `dom_interest_set_strength()`.

## Pinning (Visibility Protection)

Pin flags MUST be respected:

- `DOM_FIDELITY_PIN_VISIBLE` prevents collapse below `MICRO`.
- `DOM_FIDELITY_PIN_MISSION` and `DOM_FIDELITY_PIN_AUTHORITY` prevent collapse per policy.

Pins MUST be explicit and auditable; no implicit visibility shortcuts are allowed.

## Provenance Preservation

- `provenance_summary_hash` MUST be non-zero before any transition.
- If provenance cannot be preserved, the transition MUST be refused.
- Provenance checks are mandatory even for collapse requests.

## Hysteresis and Dwell

- `min_dwell_ticks` MUST be honored for both refine and collapse.
- Enter/exit thresholds MUST be stable and deterministic.
- Thrashing between tiers is FORBIDDEN.

## CI Enforcement

The following CI rules are mandatory:

- `SCALE-FID-001`: direct spawn/despawn/destroy patterns outside fidelity interfaces are FORBIDDEN.
- `SCALE-FID-002`: ad-hoc approximation/LOD shortcuts in authoritative code are FORBIDDEN.

See `docs/CI_ENFORCEMENT_MATRIX.md` for failure modes and remediation.

## Examples

Good (explicit refine/collapse):

```c
dom_fidelity_request_refine(&ctx, kind, id, DOM_FIDELITY_MICRO, reason);
dom_fidelity_apply_requests(&ctx, &interest, &policy, now, transitions, &count);
```

Bad (ad-hoc spawn/despawn):

```c
/* FORBIDDEN: lifecycle change bypasses fidelity */
spawn_entity(...);
```

## Implementation Checklist

- Use `dom_fidelity_request_refine()` / `dom_fidelity_request_collapse()` exclusively.
- Keep `provenance_summary_hash` non-zero for all authoritative objects.
- Respect pins before any collapse.
- Use Interest Sets to drive all refinement and collapse decisions.