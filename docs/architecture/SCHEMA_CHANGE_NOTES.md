# SCHEMA_CHANGE_NOTES

Status: binding.
Scope: required migration notes for any schema changes.

Add entries below whenever files under `schema/` change.
Each entry MUST reference the relevant invariant IDs (for example: `INV-SCHEMA-VERSIONED`,
`INV-SCHEMA-UNKNOWN-PRESERVE`, `INV-SCHEMA-NO-SEMANTIC-REUSE`).

Template:
- Date: YYYY-MM-DD
  Schema(s): schema/...
  Change: <short summary>
  Invariants: INV-...
  Migration: <required migration steps or "none">

- Date: 2026-01-31
  Schema(s): schema/knowledge.artifact.schema; schema/skill.profile.schema; schema/education.program.schema
  Change: add KNS0 knowledge, skill, and education contracts
  Invariants: INV-SCHEMA-VERSIONED; INV-SCHEMA-UNKNOWN-PRESERVE; INV-SCHEMA-NO-SEMANTIC-REUSE; INV-UNITS-ANNOTATED
  Migration: none (new schemas)

- Date: 2026-01-31
  Schema(s): schema/institution.entity.schema; schema/institution.scope.schema; schema/institution.capability.schema
  Change: add institution entities, jurisdiction scopes, and capability contracts
  Invariants: INV-SCHEMA-VERSIONED; INV-SCHEMA-UNKNOWN-PRESERVE; INV-SCHEMA-NO-SEMANTIC-REUSE; INV-UNITS-ANNOTATED
  Migration: none (new schemas)

- Date: 2026-01-31
  Schema(s): schema/logistics.container.schema; schema/logistics.storage.schema; schema/logistics.transport.schema; schema/logistics.job.schema; schema/market.place.schema; schema/market.offer.schema; schema/market.bid.schema; schema/market.transaction.schema
  Change: add logistics and market contracts for T20 economy baseline
  Invariants: INV-SCHEMA-VERSIONED; INV-SCHEMA-UNKNOWN-PRESERVE; INV-SCHEMA-NO-SEMANTIC-REUSE; INV-UNITS-ANNOTATED
  Migration: none (new schemas)

- Date: 2026-01-31
  Schema(s): schema/conflict.record.schema; schema/conflict.side.schema; schema/conflict.event.schema; schema/security_force.schema; schema/engagement.schema; schema/engagement.outcome.schema; schema/occupation.condition.schema; schema/resistance.event.schema; schema/morale.field.schema; schema/weapon.spec.schema
  Change: add conflict, engagement, occupation, morale, and weapon contracts for T21 baseline
  Invariants: INV-SCHEMA-VERSIONED; INV-SCHEMA-UNKNOWN-PRESERVE; INV-SCHEMA-NO-SEMANTIC-REUSE; INV-UNITS-ANNOTATED
  Migration: none (new schemas)

- Date: 2026-01-31
  Schema(s): schema/history.source.schema; schema/history.event.schema; schema/history.epoch.schema; schema/civilization.graph.schema; schema/civilization.node.schema; schema/civilization.edge.schema
  Change: add history and civilization graph contracts for T22 baseline
  Invariants: INV-SCHEMA-VERSIONED; INV-SCHEMA-UNKNOWN-PRESERVE; INV-SCHEMA-NO-SEMANTIC-REUSE; INV-UNITS-ANNOTATED
  Migration: none (new schemas)

- Date: 2026-01-31
  Schema(s): schema/standard.definition.schema; schema/standard.version.schema; schema/standard.scope.schema; schema/toolchain.graph.schema; schema/meta.tool.schema
  Change: add standards and meta-toolchain contracts for T23 baseline
  Invariants: INV-SCHEMA-VERSIONED; INV-SCHEMA-UNKNOWN-PRESERVE; INV-SCHEMA-NO-SEMANTIC-REUSE; INV-UNITS-ANNOTATED
  Migration: none (new schemas)

- Date: 2026-01-31
  Schema(s): schema/agent.goal.schema; schema/agent.delegation.schema; schema/agent.autonomy_budget.schema
  Change: add AI goal, delegation, and autonomy budget contracts for T24 baseline
  Invariants: INV-SCHEMA-VERSIONED; INV-SCHEMA-UNKNOWN-PRESERVE; INV-SCHEMA-NO-SEMANTIC-REUSE; INV-UNITS-ANNOTATED
  Migration: none (new schemas)

- Date: 2026-02-01
  Schema(s): schema/srz.zone.schema; schema/srz.assignment.schema; schema/srz.policy.schema; schema/process.log.schema; schema/process.hashchain.schema; schema/state.delta.schema
  Change: add SRZ execution, verification, and proof contracts
  Invariants: INV-SCHEMA-VERSIONED; INV-SCHEMA-UNKNOWN-PRESERVE; INV-SCHEMA-NO-SEMANTIC-REUSE; INV-UNITS-ANNOTATED
  Migration: none (new schemas)
