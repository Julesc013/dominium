# Action Grammar Constitution

Status: CANONICAL
Last Updated: 2026-03-03
Scope: META-ACTION-0 universal action grammar contract.

## 1) Purpose

This constitution defines a universal action grammar so every gameplay action maps to one canonical family. It prevents bespoke action systems and category drift across current and future domains.

## 2) Canonical Action Families

### 2.1 TRANSFORM

Semantic class:

- add/remove material
- change phase
- reshape
- refine
- assemble/disassemble
- bond/seal
- alter structural graph

### 2.2 MOVE

Semantic class:

- translate
- rotate
- lift/lower
- route
- schedule movement
- dock/undock
- couple/decouple

### 2.3 STORE/CONTAIN

Semantic class:

- seal/unseal
- pressurize/vent
- fill/drain
- buffer
- reserve capacity

### 2.4 SENSE/MEASURE

Semantic class:

- observe
- inspect
- sample
- calibrate
- verify compliance

### 2.5 COMMUNICATE

Semantic class:

- send
- broadcast
- relay
- encrypt/decrypt
- jam/spoof

### 2.6 DECIDE/AUTHORIZE

Semantic class:

- plan
- allocate
- approve
- certify
- enforce
- override

### 2.7 MAINTAIN

Semantic class:

- repair
- service
- reinforce
- replace
- reset wear
- inspect for service

## 3) Family Assignment Rules

Mandatory rules:

- every action exposed to player or AI maps to exactly one family
- complex actions are compositions of families, not new families
- families are ontology-neutral (no train-only/chemistry-only/biology-only families)
- no runtime mode branch may alter family semantics

ELEC-0 canonical action mapping examples:

- `connect wire` -> `TRANSFORM`
- `flip breaker` -> `DECIDE/AUTHORIZE`
- `lockout / tagout` -> `MAINTAIN`

These remain templates over existing substrates; they do not introduce electrical-only family classes.

## 4) Action Template Contract

Every action template must declare:

- required tools (`required_tool_tags`)
- required surfaces (`required_surface_types`)
- required capabilities (`required_capabilities`)
- produced artifacts (`produced_artifact_types`)
- produced hazards (`produced_hazard_types`)
- affected substrates (`affected_substrates`)
- optional constitutive-model dependencies (`uses_constitutive_model_ids`)

Allowed substrate tags:

- `Flow`
- `Field`
- `Mechanics`
- `Schedule`
- `Spec`
- `Interior`
- `Network`

If `uses_constitutive_model_ids` is declared, each referenced model ID must resolve through the constitutive model registry contract (META-MODEL).

## 5) Control Plane Contract

Control integration requirements:

- `ControlIntent.requested_action_id` must resolve through action template metadata
- control validation must enforce declared tool/surface/capability requirements
- decision logs must carry `action_family_id` for every resolved/refused action
- no direct control-path action bypasses template resolution

## 6) Compatibility Contract

The grammar is data-driven and deterministic:

- action families and templates are registry entries
- schema evolution follows CompatX semver/migration/refusal rules
- missing optional packs must degrade/refuse deterministically

## 7) Non-Goals

- no runtime action semantic changes in META-ACTION-0
- no new ontology primitives
- no nondeterministic or wall-clock behavior
