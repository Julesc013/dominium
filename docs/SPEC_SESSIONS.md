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
- `source/dominium/game/SPEC_RUNTIME.md`
