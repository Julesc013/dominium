Status: CANONICAL
Version: 1.0.0
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Compatibility: Bound to `docs/canon/glossary_v1.md` v1.0.0.

# Dominium Constitutional Architecture & Execution Contract v1

## 1) Purpose
This document is the binding constitutional contract for Dominium architecture and execution.
If any code, schema, tool, prompt, or documentation conflicts with this contract, this contract wins.

## 2) Authority Order
Apply this order when interpreting requirements:

1. `docs/canon/constitution_v1.md`
2. `docs/canon/glossary_v1.md`
3. `AGENTS.md` (repo root)
4. Schema law under `schema/` and contract docs under `docs/contracts/`
5. Architecture docs under `docs/architecture/`
6. Roadmap and testing docs

## 3) Constitutional Axioms (Non-Negotiable)

### A1. Determinism is primary
- Authoritative simulation outcomes MUST be identical for identical inputs.
- Step-by-step and batched execution MUST remain equivalent.
- Thread count, scheduler interleavings, and backend choice MUST NOT change authoritative outputs.

### A2. Process-only mutation
- Authoritative state mutation MUST occur only through deterministic Process execution.
- Direct writes outside Process commit boundaries are forbidden.
- Tooling MAY request mutation only through lawful intent/process paths.

### A3. Law-gated authority
- Capability grants permission to attempt; law determines accept/refuse/transform.
- Authority does not bypass law.
- Refusals are lawful outcomes and MUST be explicit, deterministic, and auditable.

### A4. No runtime mode flags
- Runtime behavior MUST resolve from profile data (`ExperienceProfile`, `LawProfile`, `ParameterBundle`, optional `MissionSpec` constraints).
- Hardcoded mode booleans/branches (for example `*_mode` runtime forks) are forbidden.

### A5. Event-driven advancement
- Simulation advances via scheduled events and deterministic task execution.
- Hidden background mutation and global per-tick scans that mutate state are forbidden.

### A6. Provenance is mandatory
- Creation, mutation, transfer, and destruction MUST have deterministic causal chains.
- Save/replay/audit artifacts MUST preserve that provenance.

### A7. Observer-Renderer-Truth separation
- Truth is authoritative state.
- Perception is a law/authority/lens-filtered projection.
- Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.

### A8. Engine/Game/Client/Server boundaries
- Engine defines deterministic mechanisms.
- Game defines rule meaning through engine contracts.
- Client and renderer project data and issue intents; they do not author authoritative outcomes.
- Server is authoritative in multiplayer and validates law/authority context.

### A9. Pack-driven integration
- New content and capability surfaces integrate through packs and registries.
- Packs are data-only and namespaced; executable code inside packs is forbidden.
- Missing optional packs MUST produce deterministic refusal or deterministic degradation.

### A10. Explicit degradation and refusal
- Budget pressure MAY defer/degrade/refuse.
- Silent fallback is forbidden.
- Degradation and refusal outcomes MUST be inspectable and auditable.

### A11. Absence is valid
- Systems MUST remain lawful with optional subsystems absent (for example: no AI, no economy, no war).
- Absence MUST produce explicit behavior, never hidden bypasses.

## 4) Execution Contract (EXEC0 Family)

### E1. Work IR and Access IR
- Authoritative work MUST be expressed as Work IR + Access IR contracts.
- Task ordering keys, read/write/reduce declarations, and commit points MUST be explicit.

### E2. Deterministic ordering
- Canonical commit key: `(phase_id, task_id, sub_index)`.
- Ordering decisions MUST be independent of hash-map iteration, pointer order, or thread completion order.

### E3. Deterministic reductions
- Reductions MUST use fixed-tree deterministic reduction.
- Float-based authoritative reductions are forbidden.

### E4. Named RNG streams
- Authoritative randomness MUST use named streams.
- Anonymous/global RNG and time-seeded randomness are forbidden.
- Stream naming and derivation MUST follow deterministic RNG law.

### E5. Thread-count invariance
- Authoritative outputs and partition hashes MUST remain invariant across allowed thread counts.

### E6. Replay equivalence
- Replay from authoritative logs MUST reproduce canonical authoritative hashes.
- Replay drift is a contract failure.

### E7. Hash-partition equivalence
- Canonical partitions (`HASH_SIM_CORE`, `HASH_SIM_ECON`, `HASH_SIM_INFO`, `HASH_SIM_TIME`, `HASH_SIM_WORLD`) MUST match across equivalent runs.
- Presentation hash divergence is non-authoritative unless explicitly promoted.

### E8. SRZ contract
- Execution placement (server/delegated/dormant) changes where work runs, never what law permits.
- Delegated execution requires deterministic proof artifacts before commit.

### E9. Commit legality
- Any state transition that cannot be expressed under deterministic ordering, legal authority context, and auditable commit semantics is invalid.

## 5) Compatibility, Schema, and Migration Obligations

### C1. Version semantics
- All runtime-impacting schemas MUST declare `schema_id`, `schema_version`, and `stability`.
- MAJOR changes require explicit migration routes or explicit refusal.

### C2. Skip-unknown preservation
- Unknown fields MUST round-trip unchanged where contract says open-map/extension behavior.

### C3. CompatX obligations
- Compatibility classes and migration links MUST be explicit and data-declared.
- Breaking transitions require deterministic migration specs and tests.

### C4. No silent coercion
- Migration is explicit invoke-only.
- Best-effort guessing, silent dropping, and implicit semantic defaulting are forbidden.

## 6) Testing and Invariant Obligations Per Task
Every non-trivial task MUST include:

1. Referenced invariants (by doc and section).
2. Contract impact statement (which schemas/contracts changed or confirmed unchanged).
3. Determinism impact statement (ordering, RNG, replay/hash partitions).
4. Validation execution (`FAST` at minimum, stricter when scope requires).
5. Document updates for any changed contractual behavior.

## 7) Refusal and Enforcement
- Violations of constitutional invariants require refusal or rollback of the change request.
- Workarounds that bypass invariants are forbidden.
- Constitutional conflicts are resolved by this document, not by prompt convenience.

## 8) Future Task Invocation Template
Use this prompt block for future work so tasks remain short and stable:

```text
Task ID:
Objective:
Touched Paths:
Relevant Invariants:
Required Contracts:
Required Validation Level: FAST | STRICT | FULL
Expected Artifacts:
Non-Goals:
```

## 9) Primary Cross-References
- `docs/canon/glossary_v1.md`
- `docs/architecture/ARCH0_CONSTITUTION.md`
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/EXECUTION_MODEL.md`
- `docs/architecture/EXECUTION_REORDERING_POLICY.md`
- `docs/architecture/DETERMINISTIC_REDUCTION_RULES.md`
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`
- `docs/architecture/RNG_MODEL.md`
- `docs/architecture/SRZ_MODEL.md`
- `docs/architecture/MODES_AS_PROFILES.md`
- `docs/architecture/RENDERER_RESPONSIBILITY.md`
- `docs/governance/COMPATX_MODEL.md`
- `schema/SCHEMA_VERSIONING.md`
- `schema/SCHEMA_MIGRATION.md`

