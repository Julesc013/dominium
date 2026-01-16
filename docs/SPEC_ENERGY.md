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
# Energy

- Types live in `include/domino/denergy.h`: `VoltageV` (Q16.16 volts), `Battery { capacity, stored, nominal_voltage }`, `Capacitor { capacity (ChargeC), stored, nominal_voltage }`.
- Conversions: `denergy_from_charge(q, voltage)` → `EnergyJ`; `denergy_to_charge(e, voltage)` → `ChargeC`. Integer/fixed-point only.
- Stub interfaces for machines: `denergy_request_power(agg, desired)` returns granted power (currently passthrough); `denergy_report_consumption/ generation` are hooks for accounting/telemetry.
- Integrations with networks: power network edges carry capacity and loss; generators/consumers will later bind to aggregates and networks via these stubs.
