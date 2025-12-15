# Zones and Atmospheres

- Zones represent enclosed volumes inside buildings, ships, vehicles, or underground spaces. Each zone tracks an atmosphere `Mixture` plus scalar `pressure_Pa`, `temp_K`, `volume_m3`, and leakage factors.
- `Zone { id, agg, body, atm, pressure_Pa, temp_K, volume_m3, leak_factor_0_1, thermal_leak_0_1 }` and `ZoneLink { id, a, b, area_m2, flow_coeff, flags }` (doors/vents/one-way ducts). IDs are sequential, stored in deterministic arrays (`dzone_register`, `dzone_link_register`, `dzone_get`, `dzone_link_get`).
- Tick (`dzone_tick`): for every link, compute pressure delta and move a fraction of mass between zones proportional to `flow_coeff * area * dt`; temperatures mix by mass-weighted average. Then apply leakage (`leak_factor_0_1 * dt`) to outside, thermal leakage toward body ambient, and recompute pressure from total mass and volume (idealised integer form).
- HVAC hooks: `dzone_add_gas(zone, substance, mass_delta_kg, energy_delta_J)` and `dzone_add_heat(zone, energy_delta_J)` let life support/machines inject or remove mass/heat. Behavior is deterministic and integer-only. The model is intentionally idealized (no full thermochemistry in this pass).
- Integration: Zones attach to aggregates via `agg` and to bodies via `body` for ambient defaults. No dynamic allocation during ticks; all storage is bounded arrays.
