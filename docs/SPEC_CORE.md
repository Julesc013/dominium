
# Dominium — CORE SPECIFICATION

This file defines the minimal deterministic simulation core.

---

## 1. MODULE OVERVIEW

- dom_core_types
- dom_core_mem
- dom_core_log
- dom_core_rng
- dom_core_fp
- dom_sim_tick
- dom_world_space
- dom_blueprint
- dom_network_power
- dom_network_data
- dom_network_fluids
- dom_economy
- dom_research
- dom_climate
- dom_workers

---

## 2. TICK MODEL (DETERMINISTIC)

Simulation is driven by:

- `canonical_UPS` ∈ {1,2,5,10,20,30,45,60,90,120,180,240}
- actual UPS may drop; simulation time scales accordingly
- rendering FPS decoupled

Simulation ordering must be fixed:

1. Input collection
2. Network updates (power, data, fluids)
3. Machine operations
4. Movement & transport
5. Economy & research
6. Climate/Weather
7. World state finalisation

---

## 3. RNG

A deterministic RNG with API:

struct dom_rng { uint64_t s[2]; };
void dom_rng_seed(struct dom_rng*, uint64_t seed_hi, uint64_t seed_lo);
uint32_t dom_rng_u32(struct dom_rng*);
float dom_rng_float01(struct dom_rng*);


---

## 4. WORLD STRUCTURE

Coordinates: `(x, y, z, r)`  
Chunk structure:

- Subchunk: 16×16 m  
- Chunk: 256×256 m  
- Superchunk: 4096×4096 m  
- Hyperchunk: 65536×65536 m  

World = arbitrary number of chunks, deterministic paging.

---

## 5. NETWORKS

### 5.1 Power
- DC, 1-phase AC, 3-phase AC
- voltage, current, frequency tracked per line segment
- transformers, fuses, breakers, meters supported

### 5.2 Data
- deterministic tick-based packets
- addressable nodes
- no loss; fixed latency per hop

### 5.3 Fluids
- pressure, temperature, density
- no mixing unless allowed by spec
- deterministic flow solver

---

## 6. ECONOMY

- TEU-based logistics
- Local markets per property
- Global markets per universe
- Currency system pluggable

---

## 7. RESEARCH

- science data produced by machines
- transmitted through data network
- infinite research possible
- machine tiers defined by tech level

---

## 8. CLIMATE

- monthly update
- energy balance model
- albedo, CO₂eq, forcing, ocean heat

---

## 9. WORKERS

- humans (hourly billing + experience)
- robots (upfront cost + upgradeable brains)
- pathing across networks (road, rail, air, sea)

