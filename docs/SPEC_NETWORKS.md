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
