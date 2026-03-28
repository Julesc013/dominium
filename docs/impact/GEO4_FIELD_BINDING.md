Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Change:
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

GEO-4 binds FIELD storage, sampling, and boundary exchange to GEO cell keys so ambient, pollution, and automation fields remain portable across grid, atlas, and future stub partitions.

Touched Paths:
- fields/field_engine.py
- field/field_boundary_exchange.py
- tools/xstack/sessionx/process_runtime.py
- tools/geo/tool_replay_field_geo_window.py

Demand IDs:
- fact.automated_factory
- city.stormwater_overflow_control
- surv.winter_storm_preparation

Notes:
- Factory and city simulation demand stable field transport and ambient sampling across large authored or procedural spaces.
- Survival weather exposure also depends on deterministic ambient field sampling without hardwired cartesian assumptions.
