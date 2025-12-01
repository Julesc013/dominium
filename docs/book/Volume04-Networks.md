```markdown
// docs/book/Volume04-Networks.md
# Dominium Design Book v3.0
## Volume 04 — Networks

### Overview
Dominium models interconnected deterministic networks: electrical (DC/AC), fluids/gases, data signals/packets, and transportation (road/rail/water/air/space). All networks are graph-based, integer/fixed-point, and update in the network phase before deterministic merges.

### Requirements (MUST)
- Run network updates after lane simulation and before merge; outputs merge in lane order 0..N-1.
- Electrical system supports DC, single-phase AC, and three-phase AC with fixed-point voltage/current/frequency/phase and deterministic solvers (fixed iterations, ordered traversal).
- Fluid system models liquid/gas/two-phase/special fluids as nodes/edges with volume, temperature, pressure; flows clamp to capacity using deterministic conductance.
- Data network combines continuous integer signals (per-channel) and discrete packets (fixed-size messages); packets move one hop per tick; signals have 1-tick latency.
- Transport networks use deterministic graph nodes/segments/routes for road, rail, water, air, and space; respect direction, speed/weight limits, and pathfinding determinism.
- Buffers and queues are fixed-size with oldest-drop overflow flags; no implicit loss in normal operation; backpressure throttles producers.

### Recommendations (SHOULD)
- Use fixed-point formats: e.g., voltage/current fixed24.8, resistance/reactance fixed16.16, frequency fixed16.16, phase fixed8.24.
- Keep network topology stable within a tick; rebuild/verify at tick start if needed.
- Spread heavy network updates via multi-rate schedules (fluids 2–4 ticks, heat 6 ticks, pollution 30 ticks) to balance UPS.
- Use deterministic downrating for insufficient power (ratio = gen/load) and flow clamping for fluids.

### Prohibitions (MUST NOT)
- No floating-point solvers or probabilistic routing.
- No 0-tick propagation; no random packet/flow drops.
- No lane-to-lane writes during simulation; all cross-network effects pass through queues and merge.
- No mixing of incompatible fluids unless explicitly allowed by compatibility masks.

### Detailed Sections
#### 4.1 — Network Phase in Tick Pipeline
- Networks process deterministic outputs from simulation lanes, then provide updated state for merge.
- Signals, packets, flows, and propagation fields (pollution/radiation/light/sound/air) update here using fixed traversal orders.

#### 4.2 — Electrical Power
- Graph nodes for ports; edges for conductors/transformers/switchgear; grids isolated unless connected via converters/transformers.
- Deterministic solver: build topology, iterate fixed count (e.g., 8); no dynamic convergence; integers/fixed-point complex math.
- AC/DC support arbitrary voltages/frequencies; support transformers, inverters, rectifiers, UPS/batteries, breakers/fuses/meters; downrate loads deterministically when generation < demand.

#### 4.3 — Fluids and Gases
- Domains: liquid, gas, two-phase (optional), special/cryogenic.
- Nodes/edges hold fluid slots with volume/temp/pressure/composition; flow = clamp(G*(pi-pj), -capacity, +capacity); volume/pressure updated deterministically.
- Mixing governed by compatibility masks; temperature/pressure coupling uses fixed-point; no CFD.

#### 4.4 — Data Network
- Layers: Signal (per-tick integers), Packet (addressed messages), Physical (wires/fiber/radio/satellite).
- Deterministic routing and latency: one hop per tick; queues FIFO with monotonic indices.
- Used for machine control, research data transport, automation, alerts, and interproperty comms; no packet loss unless overflow with oldest-drop flag.

#### 4.5 — Transportation Networks
- Nodes represent intersections, junctions, stations/ports/airports, tunnels/bridges, waypoints; segments represent corridors; routes define deterministic paths.
- Supports road/rail/water/air/space vehicles with deterministic pathfinding and constraints (direction, speed limit, weight).
- Integrates with logistics and workers; movement graph-driven, not free-body physics.

#### 4.6 — Buffering and Backpressure
- Fixed-size buffers for signals/packets/flows; overflow drops oldest deterministically and flags.
- Producers throttle to capacity: actual_output = min(requested, capacity); nothing is silently lost.

### Cross-References
- Volume 02 — Simulation (network phase and merge rules)
- Volume 03 — World (utility layers, spatial routing)
- Volume 05 — Economy (logistics costs, power/fuel expenses)
- Volume 06 — Climate (airflow, pollution, environmental coupling)
- Volume 07 — UIUX (network overlays, alerts, HUD readouts)
- Volume 08 — Engine (graph storage, ECS integration)
- Volume 09 — Modding (data formats for network devices and links)
```
