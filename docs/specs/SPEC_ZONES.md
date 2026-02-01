Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

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
# Zones and Atmospheres

- Zones represent enclosed volumes inside buildings, ships, vehicles, or underground spaces. Each zone tracks an atmosphere `Mixture` plus scalar `pressure_Pa`, `temp_K`, `volume_m3`, and leakage factors.
- `Zone { id, agg, body, atm, pressure_Pa, temp_K, volume_m3, leak_factor_0_1, thermal_leak_0_1 }` and `ZoneLink { id, a, b, area_m2, flow_coeff, flags }` (doors/vents/one-way ducts). IDs are sequential, stored in deterministic arrays (`dzone_register`, `dzone_link_register`, `dzone_get`, `dzone_link_get`).
- Tick (`dzone_tick`): for every link, compute pressure delta and move a fraction of mass between zones proportional to `flow_coeff * area * dt`; temperatures mix by mass-weighted average. Then apply leakage (`leak_factor_0_1 * dt`) to outside, thermal leakage toward body ambient, and recompute pressure from total mass and volume (idealised integer form).
- HVAC hooks: `dzone_add_gas(zone, substance, mass_delta_kg, energy_delta_J)` and `dzone_add_heat(zone, energy_delta_J)` let life support/machines inject or remove mass/heat. Behavior is deterministic and integer-only. The model is intentionally idealized (no full thermochemistry in this pass).
- Integration: Zones attach to aggregates via `agg` and to bodies via `body` for ambient defaults. No dynamic allocation during ticks; all storage is bounded arrays.