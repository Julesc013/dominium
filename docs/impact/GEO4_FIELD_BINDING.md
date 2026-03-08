Change:
GEO-4 binds FIELD storage, sampling, and boundary exchange to GEO cell keys so ambient, pollution, and automation fields remain portable across grid, atlas, and future stub partitions.

Touched Paths:
- src/fields/field_engine.py
- src/field/field_boundary_exchange.py
- tools/xstack/sessionx/process_runtime.py
- tools/geo/tool_replay_field_geo_window.py

Demand IDs:
- fact.automated_factory
- city.stormwater_overflow_control
- surv.winter_storm_preparation

Notes:
- Factory and city simulation demand stable field transport and ambient sampling across large authored or procedural spaces.
- Survival weather exposure also depends on deterministic ambient field sampling without hardwired cartesian assumptions.
