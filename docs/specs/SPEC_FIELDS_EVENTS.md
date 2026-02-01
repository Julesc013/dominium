Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

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
# SPEC_FIELDS_EVENTS — Fields, Events, Messages

This spec defines the deterministic communication primitives used between SIM
modules: **fields**, **events**, and **messages**. It forbids direct
cross-system calls in determinism paths.

## Scope
Applies to:
- field layers and deterministic field sampling
- event emission and routing
- message routing (including comms)
- deterministic bus/routing rules

## Definitions
- **Field**: a deterministic spatial value provider sampled at stable query
  points.
  - Output: fixed-point values only (scalar or vectorN).
  - Storage: chunk-local layers (per domain, per chunk).
- **Event**: a discrete tick-stamped record derived from simulation activity.
  - Buffered during production; delivered at a deterministic phase boundary.
- **Message**: an addressed packet sent from a source to a destination.
  - Buffered during production; delivered at a deterministic phase boundary.
  - No implicit broadcast: broadcast behavior (if needed) is expressed as a set
    of explicit messages.

## Routing and sampling invariants
- SIM modules MUST NOT call each other directly to exchange state.
  - Communication MUST flow through explicit packet/bus interfaces.
- Routing tables MUST have a canonical order (stable ID ordering).
- Field sampling MUST be deterministic:
  - sample points MUST be quantized and stable
  - multi-sample batches MUST be sorted by stable key

## Canonical ordering and phase boundaries
All three channels are **typed** (`type_id`), **TLV-backed** (payload bytes),
and **registry-driven** (optional schema validation).

### Events
- Publish/subscribe by `event_type_id` (`dg_pkt_hdr.type_id`).
- No immediate callbacks during publish.
- Delivery boundary: **PH_SENSE** (chosen for the deterministic refactor spine).
- Canonical event sort key (ascending):
  - `(tick, type_id, src_entity, dst_entity, seq)`
- Subscriber delivery order per event:
  - `(subscriber_priority_key, registration_order)`
- Budgeting:
  - 1 work unit per subscriber delivery.
  - If budget is exhausted, remaining deliveries are deferred deterministically
    (carryover work queues); no loss.

### Messages
- Addressed destination is expressed as stable numeric IDs (entity/group/endpoint
  id space).
- No implicit broadcast unless expanded into explicit messages.
- Delivery boundary: **PH_SENSE**.
- Canonical message sort key (ascending):
  - `(tick, dst_entity, type_id, src_entity, seq)`
- Subscriber delivery order per message:
  - `(subscriber_priority_key, registration_order)`
- Budgeting:
  - 1 work unit per subscriber delivery.
  - Budget exhaustion defers remaining deliveries deterministically; no loss.

### Fields
- Fields are registered by `field_type_id` (`dg_pkt_hdr.type_id`).
- Updates are applied via field update packets (`dg_pkt_field_update`).
  - Updates are buffered; never applied immediately.
  - Apply boundary: **PH_SENSE** update substep (runs before sampling).
  - Canonical update sort key (ascending):
    - `(tick, domain_id, chunk_id, field_type_id, seq)`
- Sampling:
  - Sampling occurs in **PH_SENSE** only.
  - Sampling kernels MUST use a fixed neighbor order and fixed arithmetic
    weights (no adaptive kernels, no tolerances).
- Budgeting:
  - Field update application and field sampling consume deterministic work
    units; excess work is deferred deterministically.

## Probes (instrumentation)
Routing/sampling implementations SHOULD expose lightweight counters (no logging),
such as:
- events published / delivered
- messages delivered
- field updates applied
- field samples performed
- deferred deliveries/work count

## Determinism guarantees
- No unordered iteration or pointer-ordered fanout.
- No platform time sources or IO in routing/sampling.
- All values are fixed-point; any external float input MUST be quantized before
  entering deterministic paths.

## Forbidden behaviors
- Implicit global dispatch based on pointer identity or hash iteration.
- UI-driven state mutation (UI/tools emit intents only; see `docs/specs/SPEC_ACTIONS.md`).
- Platform-dependent behavior in routing (thread timing, network timing).

## Source of truth vs derived cache
**Source of truth:**
- authoritative state + delta stream
- intent streams for commanded messages (if applicable)

**Derived cache:**
- field sample caches
- emitted events/messages/observations (reproducible outputs)

## Related specs
- `docs/specs/SPEC_DETERMINISM.md`
- `docs/specs/SPEC_PACKETS.md`
- `docs/specs/SPEC_ACTIONS.md`
- `docs/specs/SPEC_SIM_SCHEDULER.md`
- `docs/specs/SPEC_KNOWLEDGE_VIS_COMMS.md`