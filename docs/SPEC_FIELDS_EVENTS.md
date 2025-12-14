# SPEC_FIELDS_EVENTS — Fields, Events, Messages

This spec defines the deterministic communication primitives used between SIM
modules: fields, events, and messages. It forbids direct cross-system calls in
determinism paths.

## Scope
Applies to:
- field layers and deterministic field sampling
- event emission and routing
- message routing (including comms)
- deterministic bus/routing rules

## Definitions
- **Field**: a deterministic value provider sampled at stable query points.
  - Inputs: `(tick, domain_id, frame_id, sample_key, params)`
  - Output: fixed-point values only
- **Event**: a discrete tick-stamped record derived from committed state.
- **Message**: a directed/broadcast communication object routed deterministically.

## Routing and sampling invariants
- SIM modules MUST NOT call each other directly to exchange state.
  - Communication MUST flow through explicit packet/bus interfaces.
- Routing tables MUST have a canonical order (stable ID ordering).
- Field sampling MUST be deterministic:
  - sample points MUST be quantized and stable
  - multi-sample batches MUST be sorted by stable key

## Determinism guarantees
- No unordered iteration or pointer-ordered fanout.
- No platform time sources or IO in routing/sampling.
- All values are fixed-point; any external float input MUST be quantized before
  entering deterministic paths.

## Forbidden behaviors
- Implicit global dispatch based on pointer identity or hash iteration.
- UI-driven state mutation (UI/tools emit intents only; see `docs/SPEC_ACTIONS.md`).
- Platform-dependent behavior in routing (thread timing, network timing).

## Source of truth vs derived cache
**Source of truth:**
- authoritative state + delta stream
- intent streams for commanded messages (if applicable)

**Derived cache:**
- field sample caches
- emitted events/messages/observations (reproducible outputs)

## Related specs
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_PACKETS.md`
- `docs/SPEC_ACTIONS.md`
- `docs/SPEC_SIM_SCHEDULER.md`
- `docs/SPEC_KNOWLEDGE_VIS_COMMS.md`

