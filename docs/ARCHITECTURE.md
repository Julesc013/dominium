Status: DERIVED
Last Reviewed: 2026-02-13
Supersedes: none
Superseded By: none

# Dominium Architecture

This document summarizes the active architecture across engine, game, products, and governance execution.

Canonical contracts remain in `docs/architecture/`, starting with `docs/architecture/ARCH0_CONSTITUTION.md`.

## System Layers

```
                         +----------------------+
                         |   RepoX / TestX      |
                         |   AuditX / XStack    |
                         +----------+-----------+
                                    |
+----------------+     +------------v------------+     +----------------+
|   Client/UI    |<--->|   Server (authority)    |<--->| Launcher/Setup |
| presentation   |     | sessions + validation   |     | orchestration  |
+--------+-------+     +------------+------------+     +--------+-------+
         |                            |                          |
         +----------------------------v--------------------------+
                              Game (C++98)
                       meaning + process orchestration
                                      |
                                      v
                             Engine (C89 core)
                   deterministic substrate + canonical state
```

## Engine vs Game vs Client vs Server

- `engine/`: deterministic kernel and core runtime APIs.
- `game/`: rules and world behavior on top of engine APIs.
- `client/`: command and UI projection; not authoritative source of truth.
- `server/`: authoritative intent/law checks in multiplayer paths.

The layering and boundaries are documented in:

- `docs/architecture/CANONICAL_SYSTEM_MAP.md`
- `docs/architecture/SERVICES_AND_PRODUCTS.md`
- `docs/architecture/EXECUTION_MODEL.md`

## Session Identity and Authority Context

Session composition is explicit and schema-driven:

- `schema/session/session_spec.schema`
- `schema/authority/authority_context.schema`

`SessionSpec` includes `experience_id`, `parameter_bundle_id`, `pack_lock_hash`, and `authority_context`.  
`AuthorityContext` carries law binding, entitlements, origin (`client|server|tool|replay`), and server-authoritative flags.

Relevant registries:

- `data/registries/session_defaults.json`
- `data/registries/experience_profiles.json`
- `data/registries/law_profiles.json`
- `data/registries/parameter_bundles.json`

## Universe Identity vs Universe State

Universe lifecycle is split:

- immutable root identity: `schema/universe/universe_identity.schema`
- mutable runtime/save state: `schema/universe/universe_state.schema`

This separation preserves deterministic migration and replay boundaries.

## Experiences, LawProfiles, and Parameter Bundles

Profiles are data-driven:

- Experience schema: `schema/meta/experience_profile.schema`
- Law schema: `schema/law/law_profile.schema`
- Parameter bundle schema: `schema/meta/parameter_bundle.schema`
- Bundle schema: `schema/meta/bundle_profile.schema`

Key registries:

- `data/registries/experience_profiles.json`
- `data/registries/law_profiles.json`
- `data/registries/parameter_bundles.json`
- `data/registries/bundle_profiles.json`

No runtime mode branching is required when profile bindings are complete.

## Session Pipeline and Lifecycle

Client lifecycle is pipeline-based and command-driven:

- `schema/client/session_pipeline.schema`
- `schema/client/session_artifacts.schema`
- `client/core/session_pipeline.c`
- `client/core/session_stage_registry.c`
- `client/core/session_refusal_codes.c`

Canonical stages include `ResolveSession`, `AcquireWorld`, `VerifyWorld`, warmup stages, `SessionReady`, and `SessionRunning`.

## Macro Capsule Contract (Collapse/Expand)

Macro-level compression and refinement are contract-based, not ad-hoc:

- `schema/macro_capsule.schema`
- `data/registries/solver_registry.json`

The macro capsule contract records invariants, statistics, provenance, and reconstruction seeds required for deterministic expand/collapse transitions.

## Domain and Solver Architecture

Domain declarations are schema-defined:

- `schema/domain.schema`

Solver metadata and guarantees are registry-defined:

- `data/registries/solver_registry.json`

Runtime selection is constrained by deterministic ordering, guarantees, and refusal codes recorded in solver metadata.

## Truth / Perceived / Render Models

The model boundary is:

```
TruthModel --(LawProfile + AuthorityContext + Lens)--> PerceivedModel --> RenderModel
```

`TruthModel` is canonical state. `PerceivedModel` is entitlement/law filtered projection.  
`RenderModel` is UI/backend-targeted projection for CLI/TUI/GUI.

Reference docs:

- `docs/architecture/REALITY_MODEL.md`
- `docs/architecture/EPISTEMICS_MODEL.md`
- `docs/architecture/RENDERER_RESPONSIBILITY.md`

## SRZ-0 Scaling

SRZ (Simulation Responsibility Zone) partitioning defines scale ownership and deterministic partition behavior:

- `docs/architecture/SRZ_MODEL.md`
- `schema/srz.zone.schema`
- `schema/srz.assignment.schema`
- `schema/srz.policy.schema`

## Determinism and Replay

Determinism and replay are enforced via:

- explicit process mutation contracts
- deterministic scheduler/order guarantees
- canonical artifact hashes
- TestX replay and determinism suites

References:

- `docs/architecture/INVARIANTS.md`
- `docs/governance/TESTX_ARCHITECTURE.md`
- `schema/save_and_replay.schema`
- `schema/process.log.schema`

## World Representation

World shape and initial state contracts:

- `schema/world_definition.schema`
- `schema/topology.schema`
- `schema/field.schema`
- `schema/assembly.schema`

World definitions are declarative and provenance-tagged; runtime behavior is enforced by process/law execution, not by world file assumptions.

## Worldgen Summary

Worldgen contracts and registry:

- `schema/worldgen/worldgen_module.schema`
- `schema/worldgen/worldgen_plan.schema`
- `schema/worldgen/world_spec.schema`
- `schema/worldgen/universe_spec.schema`
- `data/registries/worldgen_module_registry.json`

Current module registry includes active baseline modules (`org.dominium.worldgen.terrain_base`, `org.dominium.worldgen.hydrology`) plus explicit experimental stubs with refusal paths.

Related runtime/tooling:

- `tools/worldgen_offline/world_definition_cli.py`
- `tools/worldgen_offline/refinement_runner.py`

## Related Docs

- Governance execution: `docs/XSTACK.md`
- Survival baseline: `docs/SURVIVAL_SLICE.md`
- Canon glossary: `docs/GLOSSARY.md`
