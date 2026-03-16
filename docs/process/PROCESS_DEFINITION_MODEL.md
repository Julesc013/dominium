Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Process Definition Model

Status: CANONICAL  
Last Updated: 2026-03-06  
Scope: PROC-1 ProcessDefinition schemas, deterministic validation, and canonical run records.

## 1) Step Graph

A `ProcessDefinition` is a deterministic directed acyclic graph (DAG) of typed steps.

### Step kinds
- `action_step`
  - Player/agent task-gated work.
  - Must map to META-ACTION via `action_template_id`.
- `transform_step`
  - Domain process invocation (CHEM/FLUID/THERM/ELEC or other registered process pathways).
  - Mutation remains process-only.
- `measure_step`
  - Observation production.
  - Produces INFO-family `OBSERVATION` artifacts.
- `verify_step`
  - Compliance/safety/spec verification.
  - Produces INFO-family `REPORT` artifacts.
- `wait_step`
  - Temporal-domain condition gate.
  - Binds to TEMP temporal domains.

### Step declaration requirements
Each step must declare:
- required inputs (typed references)
- produced outputs (typed references)
- `cost_units`
- tier applicability (directly or via process/tier contract binding)

### Deterministic ordering
- Graph must be acyclic.
- Execution order derives from stable topological sort.
- Tie-break must be stable by `step_id`.

## 2) Versioning

`ProcessDefinition` is versioned and CompatX-governed.

Required behavior:
- explicit `version`
- stable deterministic fingerprint over normalized payload
- schema-driven validation with explicit refusal on invalid/missing fields
- migration path or refusal path for incompatible versions

No silent coercion is allowed.

## 3) Canonical Run Records

A `ProcessRun` is authoritative and emits canonical `RECORD` artifacts.

### Canonical run lifecycle events
- `run_started`
- `step_completed` (and step status progression records)
- `run_completed`

### Required run references
A run record must carry deterministic references to:
- input batch IDs / refs
- output batch IDs / refs
- tool IDs
- bounded environment state snapshots

### Deterministic execution obligations
- process-only mutation
- deterministic ordering
- no wall-clock dependencies
- named RNG only if explicitly declared by policy (not enabled by PROC-1 defaults)

### Ledger and accounting obligations
For transform steps that move mass/energy:
- PHYS energy transforms must be ledgered
- entropy increments must be recorded
- emissions must be recorded via pollutant/emission pathways
- direct mutation without ledger/provenance entry is refusal

## 4) Non-Goals in PROC-1
- No yield/defect distribution implementation (PROC-2).
- No ProcessCapsule runtime abstraction (PROC-5).
- No stochastic process behavior by default.

PROC-1 only establishes deterministic ProcessDefinition and ProcessRun infrastructure.
