# Simulation Coverage Ladder (COVERAGE-0)

Status: binding.
Scope: long-term simulation capability targets expressed as tests and docs only.

Coverage levels are developer goals, test targets, and documentation milestones.
They are NOT runtime constructs. Engine/game code MUST NOT branch on coverage,
era, or progression.

## Coverage Levels

C-A — Abiotic world
Fields, terrain, climate, energy, and physical processes. No life required.

C-B — Simple life
Reproduction as processes, resource-limited growth, no cognition required.

C-C — Animals
Agent possession, movement, feeding, and death. No abstract planning required.

C-D — Proto-culture
Social coordination, lossy knowledge artifacts, minimal institutions.

C-E — Symbolic knowledge
Standards, instruments, and persistent knowledge artifacts.

C-F — Civilization
Trade networks, law and institutions, infrastructure and logistics.

C-G — Systemic stress and collapse
Resource depletion, institutional failure, recovery or extinction paths.

C-H — Post-human or speculative
Non-human cognition, alternate physics, meta-civilizations.

## Rules (Non-Negotiable)

- Coverage levels MUST NOT appear in engine or game code.
- Coverage levels MUST NOT be referenced by content logic.
- Coverage levels MAY be referenced by tests and docs only.
- Capability gating remains the only valid enforcement mechanism.

## Coverage → Test Mapping (Authoritative)

| Level | Required schemas | Required process families | Required capability IDs | Required refusal behavior |
| --- | --- | --- | --- | --- |
| C-A | schema/domain.schema<br>schema/field.schema<br>schema/interface.schema<br>schema/material.schema<br>schema/process_family.schema<br>schema/topology.schema<br>schema/world_definition.schema<br>schema/worldgen_model.schema | org.dominium.coverage.c-a.process.decay<br>org.dominium.coverage.c-a.process.transfer<br>org.dominium.coverage.c-a.process.transform | org.dominium.coverage.c-a.fields<br>org.dominium.coverage.c-a.materials<br>org.dominium.coverage.c-a.processes<br>org.dominium.coverage.c-a.worldgen | REFUSE_CAPABILITY_MISSING<br>WD-REFUSAL-CAPABILITY |
| C-B | schema/assembly.schema<br>schema/batch_lot.schema<br>schema/domain.schema<br>schema/field.schema<br>schema/material.schema<br>schema/part.schema<br>schema/process_family.schema<br>schema/quality.schema<br>schema/substance.schema<br>schema/topology.schema<br>schema/world_definition.schema<br>schema/worldgen_model.schema | org.dominium.coverage.c-b.process.consume<br>org.dominium.coverage.c-b.process.repair<br>org.dominium.coverage.c-b.process.reproduce | org.dominium.coverage.c-b.growth<br>org.dominium.coverage.c-b.processes<br>org.dominium.coverage.c-b.reproduction<br>org.dominium.coverage.c-b.resources | REFUSE_CAPABILITY_MISSING<br>WD-REFUSAL-CAPABILITY |
| C-C | schema/assembly.schema<br>schema/authority.schema<br>schema/domain.schema<br>schema/field.schema<br>schema/material.schema<br>schema/measurement_artifact.schema<br>schema/network.schema<br>schema/part.schema<br>schema/process.schema<br>schema/process_family.schema<br>schema/quality.schema<br>schema/topology.schema<br>schema/world_definition.schema<br>schema/worldgen_model.schema | org.dominium.coverage.c-c.process.die<br>org.dominium.coverage.c-c.process.feed<br>org.dominium.coverage.c-c.process.move<br>org.dominium.coverage.c-c.process.possess | org.dominium.coverage.c-c.agents<br>org.dominium.coverage.c-c.death<br>org.dominium.coverage.c-c.feeding<br>org.dominium.coverage.c-c.movement | REFUSE_CAPABILITY_MISSING<br>WD-REFUSAL-CAPABILITY |
| C-D | schema/authority.schema<br>schema/domain.schema<br>schema/field.schema<br>schema/institution.schema<br>schema/knowledge.schema<br>schema/material.schema<br>schema/network.schema<br>schema/process_family.schema<br>schema/topology.schema<br>schema/world_definition.schema<br>schema/worldgen_model.schema | org.dominium.coverage.c-d.process.communicate<br>org.dominium.coverage.c-d.process.coordinate<br>org.dominium.coverage.c-d.process.record-lossy | org.dominium.coverage.c-d.coordination<br>org.dominium.coverage.c-d.institutions<br>org.dominium.coverage.c-d.knowledge.lossy<br>org.dominium.coverage.c-d.social | REFUSE_CAPABILITY_MISSING<br>WD-REFUSAL-CAPABILITY |
| C-E | schema/domain.schema<br>schema/instrument.schema<br>schema/knowledge.schema<br>schema/measurement_artifact.schema<br>schema/process_family.schema<br>schema/quality.schema<br>schema/standard.schema<br>schema/topology.schema<br>schema/world_definition.schema<br>schema/worldgen_model.schema | org.dominium.coverage.c-e.process.calibrate<br>org.dominium.coverage.c-e.process.inspect<br>org.dominium.coverage.c-e.process.standardize | org.dominium.coverage.c-e.instruments<br>org.dominium.coverage.c-e.knowledge.symbolic<br>org.dominium.coverage.c-e.measurement<br>org.dominium.coverage.c-e.standards | REFUSE_CAPABILITY_MISSING<br>WD-REFUSAL-CAPABILITY |
| C-F | schema/authority.schema<br>schema/capability_lockfile.schema<br>schema/domain.schema<br>schema/institution.schema<br>schema/knowledge.schema<br>schema/process_family.schema<br>schema/refinement_plan.schema<br>schema/standard.schema<br>schema/topology.schema<br>schema/world_definition.schema<br>schema/worldgen_model.schema | org.dominium.coverage.c-f.process.adjudicate<br>org.dominium.coverage.c-f.process.exchange<br>org.dominium.coverage.c-f.process.infra-maintain<br>org.dominium.coverage.c-f.process.logistics | org.dominium.coverage.c-f.infrastructure<br>org.dominium.coverage.c-f.law<br>org.dominium.coverage.c-f.logistics<br>org.dominium.coverage.c-f.trade | REFUSE_CAPABILITY_MISSING<br>WD-REFUSAL-CAPABILITY |
| C-G | schema/budget_policy.schema<br>schema/budget_snapshot.schema<br>schema/hazard.schema<br>schema/institution.schema<br>schema/process_family.schema<br>schema/refinement_plan.schema<br>schema/shard_lifecycle.schema<br>schema/world_definition.schema<br>schema/worldgen_model.schema | org.dominium.coverage.c-g.process.collapse<br>org.dominium.coverage.c-g.process.degrade<br>org.dominium.coverage.c-g.process.recover | org.dominium.coverage.c-g.collapse<br>org.dominium.coverage.c-g.depletion<br>org.dominium.coverage.c-g.failure<br>org.dominium.coverage.c-g.recovery | REFUSE_CAPABILITY_MISSING<br>WD-REFUSAL-CAPABILITY |
| C-H | schema/cross_shard_message.schema<br>schema/macro_capsule.schema<br>schema/macro_event_queue.schema<br>schema/macro_schedule.schema<br>schema/process_family.schema<br>schema/topology.schema<br>schema/world_definition.schema<br>schema/worldgen_model.schema | org.dominium.coverage.c-h.process.alternate-physics<br>org.dominium.coverage.c-h.process.meta-civilization<br>org.dominium.coverage.c-h.process.nonhuman-cognition | org.dominium.coverage.c-h.alternate-physics<br>org.dominium.coverage.c-h.meta-civilizations<br>org.dominium.coverage.c-h.nonhuman-cognition<br>org.dominium.coverage.c-h.speculative-systems | REFUSE_CAPABILITY_MISSING<br>WD-REFUSAL-CAPABILITY |

## See also
- `docs/roadmap/ROADMAP_OVERVIEW.md`
- `docs/roadmap/SLICE_VS_COVERAGE.md`
