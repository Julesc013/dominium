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
- None. Game consumes engine primitives where applicable.

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
# Networks

- Network kinds: `NET_POWER`, `NET_FLUID`, `NET_GAS`, `NET_HEAT`, `NET_SIGNAL`, `NET_DATA`, `NET_COMM`. Nodes are generic `{ id, kind }`; edges are per-kind structs in `include/domino/dnet.h`.
- Edge semantics:
  - Power: `{ capacity, loss_factor_0_1, flow }` (`PowerW`, Q16.16 loss).
  - Fluid/Gas: `{ capacity_per_s, friction_factor, flow_per_s }` (`VolM3`, Q16.16 friction).
  - Heat: `{ capacity, conductance, transfer }` (`EnergyJ`, Q16.16 conductance).
  - Signal/Data/Comm: `{ latency_s (SecondsQ16), bandwidth_bps (Q16.16), reliability_0_1 }`.
- API: `dnet_register_node(kind)`; per-kind `dnet_register_*_edge(def)` plus getters. Registries are bounded arrays for deterministic storage.
- Solvers (stubbed): `dnet_power_step`, `dnet_fluid_step`, `dnet_gas_step`, `dnet_heat_step`, `dnet_signal_step`, `dnet_data_step`, `dnet_comm_step`. Current behaviour applies simple loss/friction/conductance calculations; signal/data/comm no-op for now.
- Numeric policy: no floats; all capacities/flows/losses use fixed-point types from `dnumeric.h`.