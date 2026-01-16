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
# SPEC_INPUT — Input Plumbing and Deterministic Simulation Boundary

This spec defines the input boundary contract: how platform input is collected
and how (and where) it is allowed to influence deterministic simulation.

It is not a keybinding UX document.

## Scope
Applies to:
- platform event ingestion (`dsys_event`)
- input state aggregation (`dom_input_state`)
- the boundary between input/UI and deterministic SIM (`dg_pkt_intent`)

## Layer responsibilities (authoritative)
### Platform/system layer
- Location: `source/domino/system/**`, public header `include/domino/sys.h`.
- Owns OS/window/event polling and produces `dsys_event` records.
- Platform time and event timing are non-deterministic and MUST NOT be used as
  inputs to deterministic simulation decisions.

### Input aggregation layer
- Location: `source/domino/input/**`, public header `include/domino/input.h`.
- Owns `dom_input_state` (keys, mouse, basic gamepad state).
- `dom_input_reset` and `dom_input_consume_event` fold `dsys_event` into
  `dom_input_state`.
- High-level mapping helpers are stubbed in this pass:
  - `dom_input_axis(name)` returns `0.0f`
  - `dom_input_action(name)` returns `false`

### Product/UI layer (Dominium)
- Location: `source/dominium/**`.
- Owns any user-facing action mapping, UI state machines, and tool/editor input.
- The only permitted way to affect deterministic simulation is to emit
  deterministic intents (`dg_pkt_intent`) into the SIM input stream
  (`docs/SPEC_ACTIONS.md`, `docs/SPEC_PACKETS.md`).

### Deterministic SIM layer
- Location: `source/domino/sim/**`.
- MUST NOT read platform input directly.
- Consumes only deterministic, tick-grouped command streams (intents) and
  produces deterministic deltas/events/messages at scheduler phase boundaries.

## Determinism rules
- Any input that affects simulation MUST be represented as a deterministic
  command stream grouped by tick (intents).
- UI conveniences such as snapping, smoothing, camera-driven selection, and
  viewport state are non-authoritative and MUST NOT affect simulation unless
  explicitly encoded into intents as quantized fixed-point parameters.
- Raw platform events and `dom_input_state` are never hashed as part of the
  authoritative world hash.

## Forbidden behaviors
- Deterministic simulation code calling OS/platform APIs for input.
- Using wall-clock timestamps as simulation inputs.
- Treating UI state (camera, selection, framerate) as authoritative state.

## Related specs
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_ACTIONS.md`
- `docs/SPEC_PACKETS.md`
- `docs/SPEC_SIM_SCHEDULER.md`
- `docs/SPEC_DOMINO_AUDIO_UI_INPUT.md`
