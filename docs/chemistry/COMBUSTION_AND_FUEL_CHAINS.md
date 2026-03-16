Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Combustion and Fuel Chains

Status: CANONICAL
Last Updated: 2026-03-05
Scope: CHEM-1 deterministic combustion and fuel-chain contract.

## 1) Purpose

Define deterministic, model-driven combustion and fuel-chain behavior that:

- converts chemical energy into thermal/electrical accounting channels only through registered PHYS-3 transforms,
- logs pollutant emissions as explicit RECORD artifacts,
- links irreversibility to entropy policy,
- preserves process-only mutation and replay determinism.

This document extends existing THERM fire hooks without introducing a full kinetics solver.

## 2) Combustion Profile Contract

Combustion is represented by a `ReactionProfile`-style row:

- `input_species`
  - fuel
  - oxidizer
- `output_species`
  - exhaust_gas
  - residue
- `energy_transformation_id`
  - `transform.chemical_to_thermal`
- `emission_species`
  - `pollutant_coarse` (stub for POLL-0 intake)

Combustion and explosive variants are deterministic profile selections, not runtime mode branches.

## 3) Efficiency Contract

Combustion efficiency is model-driven:

`efficiency_permille = f(temperature, entropy_index, mixture_ratio_stub)`

Normative behavior:

- `chemical_energy_in * efficiency_permille / 1000 -> quantity.energy_thermal`
- unconverted share contributes to irreversibility/entropy pathways.
- no silent direct writes to energy totals.

## 4) Fuel Chain Routing

Chemical chain outputs may be routed to:

- THERM:
  - heat input for exchanger/boiler style behavior
  - loss-to-heat convention preserved (`quantity.heat_loss` pathway)
- ELEC (hook):
  - `transform.chemical_to_electrical` may be used for generator-bound assemblies
  - no generator solver behavior change required in CHEM-1

## 5) Emissions Contract

Combustion emissions must:

- be emitted as pollutant-tagged mass quantities (coarse POLL hook),
- produce deterministic RECORD artifacts,
- remain replay-verifiable and proof-hashable.

POLL solver behavior is out of scope for CHEM-1.

## 6) Safety and Failure Hooks

Combustion may trigger:

- `hazard.overheat` escalation
- `hazard.fire.basic` continuation/escalation

Explosive profile behavior (stub):

- rapid chemical transform with bounded impulse hook
- impulse routed through PHYS process path (`process.apply_impulse`)
- no direct velocity mutation and no bespoke physics solver

## 7) Tiering and Determinism

Combustion evaluation remains tiered and deterministic:

- C0 fallback: instant burn bookkeeping with explicit downgrade logs
- C1 baseline: deterministic rate/profile evaluation
- C2 reserved: ROI refinement (future)

Forbidden:

- wall-clock dependence
- nondeterministic RNG use without named stream policy
- direct energy/mass mutation bypassing process+ledger pathways

## 8) Canonical Invariants Upheld

- A1 Determinism is primary
- A2 Process-only mutation
- A6 Provenance is mandatory
- PHYS-3 energy transform registration and ledger entry requirements
- META-CONTRACT coupling/explain contract requirements

## 9) Non-goals

- full chemistry kinetics/equilibrium
- mandatory POLL simulation
- full generator simulation redesign
- solver-level thermodynamic expansion

## 10) Proof and Replay Hooks

Combustion truth surfaces must expose deterministic chains:

- `combustion_hash_chain`
- `emission_hash_chain`
- `impulse_hash_chain` (when explosive profiles emit impulse hooks)

Control proof bundles include these chains for tick windows where combustion rows are present.
Replay verification tool:

- `tools/chem/tool_replay_combustion_window` (plus `.py`/`.cmd`)

## 11) Enforcement Hooks

RepoX strict blockers:

- `INV-COMBUSTION-THROUGH-REACTION-ENGINE`
- `INV-ENERGY-TRANSFORM-REGISTERED`
- `INV-NO-DIRECT-FUEL-DECREMENT`

AuditX strict analyzers:

- `E242_INLINE_FUEL_BURN_SMELL`
- `E243_UNREGISTERED_COMBUSTION_SMELL`
