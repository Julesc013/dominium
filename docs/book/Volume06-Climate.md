```markdown
// docs/book/Volume06-Climate.md
# Dominium Design Book v3.0
## Volume 06 — Climate

### Overview
Climate and weather are deterministic, chunk-scaled simulations governing temperature, atmosphere, wind, solar flux, precipitation, and hydrology. They operate across planet/continent/area/property layers using fixed-point data, influencing energy, agriculture, building loads, and worker health.

### Requirements (MUST)
- Maintain EnvCell per 16×16 m subchunk storing fixed-point temp, humidity, rainfall, wind speed/direction, solar flux, cloud cover, pressure.
- Define climate zones per 256 km × 256 km area (tropical, arid, temperate, continental, polar, highland, oceanic, tundra, desert); blend transitions deterministically.
- Use multi-layer model: planet (base temp, axial tilt, orbital period, atmosphere, greenhouse/solar constants), continent/area (biome, elevation, humidity baseline, winds, storm probability), property (microclimate).
- Update climate/weather deterministically (monthly climate ticks per SPEC-core; weather/hydrology via multi-rate schedules).
- Hydrology covers surface/underground water, flow, evaporation, rainfall/snow/storms; erosion affects terrain deterministically.
- Outputs drive solar/wind generation, HVAC loads, fluid condensation, agriculture, worker comfort, machine cooling.

- Use integer/fixed-point math; no floating-point or stochastic weather.

### Recommendations (SHOULD)
- Diffuse pollution/radiation/sound/light via symmetric kernels on slower schedules.
- Tie extreme weather events to deterministic thresholds in climate descriptors.
- Cache area-level climate envelopes for fast property updates.

### Prohibitions (MUST NOT)
- No random weather or platform-dependent noise; all variability derives from seeded deterministic processes.
- No environment-driven state changes outside tick phases.
- No unbounded data growth; grids and histories are bounded and chunked.

### Detailed Sections
#### 6.1 — Environmental Data Grid
- EnvCell fixed-point schema per subchunk; stored in chunk metadata; used by networks, workers, and UI overlays.
- Updated on scheduled ticks; immutable between phases for determinism.

#### 6.2 — Climate Layers
- Planet layer defines base atmospheric constants and solar forcing.
- Continent/area layers define biome/weather envelopes and prevailing winds.
- Property layer applies microclimate variance; inherits area climate.

#### 6.3 — Weather and Seasonal Cycles
- Deterministic generation for rainfall/snow/storms, cloud cover, day/night lighting; supports axial tilt and orbital period per planet.
- Climate tick monthly; weather updated on configured multi-rate schedule; no stochastic inputs.

#### 6.4 — Hydrology and Environment Interaction
- Tracks surface flow, underground water tables, evaporation; integrates with terrain and construction (flooding risk, water collection).
- Influences fluid networks (water/steam), agriculture, and cooling systems.

#### 6.5 — Pollution and Environmental Fields
- Pollution, radiation, sound, light propagate with deterministic diffusion/decay kernels; scheduling aligned with slower ticks.
- Impacts worker health and building loads; connects to data/HUD for alerts.

### Cross-References
- Volume 02 — Simulation (multi-rate schedules, deterministic kernels)
- Volume 03 — World (terrain, environment grid, hydrology storage)
- Volume 04 — Networks (fluid/airflow interaction, power generation)
- Volume 05 — Economy (resource yields, costs tied to environment)
- Volume 07 — UIUX (weather overlays, alerts)
- Volume 08 — Engine (persistence of EnvCell data)
- Volume 09 — Modding (planet/biome/climate definitions in packs)
```
