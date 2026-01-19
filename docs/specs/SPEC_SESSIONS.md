--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

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
# SPEC_SESSIONS — Session Roles and Authority Modes

## Scope
Defines session roles, authority modes, and required invariants for the game
runtime session layer.

## Session roles
- **SINGLE:** local loopback session using server-auth internally.
- **HOST:** listens for clients; may run server-auth or lockstep.
- **DEDICATED_SERVER:** headless server-auth only.
- **CLIENT:** connects to a host; may run server-auth or lockstep.

## Authority modes
- **SERVER_AUTH:** server simulation is authoritative; clients receive
  snapshots/deltas and do not author authoritative state.
- **LOCKSTEP:** peers simulate deterministically; exchange commands and hashes.

Authority mode is fixed for the session lifetime.

Cosmos-lane travel state is authoritative and must follow the selected
authority mode for command/hash exchange and refusal behavior. See
`docs/SPEC_COSMO_LANE.md` and `docs/SPEC_LOGICAL_TRAVEL.md`.

## Session flags
Session configuration carries launcher-provided flags and negotiation toggles:
- **SAFE_MODE / OFFLINE_MODE:** launcher-defined policy flags (pass-through).
- **REQUIRE_UI:** indicates a UI frontend is required.
- **ENABLE_COMMANDS / ENABLE_HASH_EXCHANGE:** required for lockstep exchanges;
  ignored by server-auth where applicable.

## Loopback singleplayer
Singleplayer uses the same code paths as networked play:
- SINGLE sessions run HOST + CLIENT in-process via a loopback driver.
- This enforces identical command and snapshot paths.

## QoS and assistance layer
QoS negotiation is optional and non-sim; see `docs/SPEC_QOS_ASSISTANCE.md`.
SERVER_AUTH uses QoS to adjust snapshot cadence/detail and interest radius.
LOCKSTEP uses QoS for diagnostics cadence only; authority never moves.

## Validation requirements
Session configuration MUST reject:
- SINGLE or DEDICATED_SERVER with LOCKSTEP authority.
- CLIENT without a connect address.
- DEDICATED_SERVER when REQUIRE_UI is set.
- LOCKSTEP when command/hash exchange is disabled.
- zero tick rate or invalid port values.

Session configuration MUST ensure:
- SINGLE does not require external network access (no connect address).
- CLIENT in SERVER_AUTH never advances authoritative simulation state.

## Related specs
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_QOS_ASSISTANCE.md`
- `docs/SPEC_COSMO_LANE.md`
- `docs/SPEC_LOGICAL_TRAVEL.md`
- `source/dominium/game/SPEC_RUNTIME.md`
