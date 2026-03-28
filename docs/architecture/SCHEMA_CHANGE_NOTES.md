Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

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

- Date: 2026-03-11
  Schema(s): schema/lib/bundle_manifest.schema; schema/lib/bundle_item.schema
  Change: add LIB-6 deterministic bundle manifest and ordered bundle item contracts for export/import tooling
  Invariants: INV-SCHEMA-VERSION-BUMP; INV-BUNDLES-DETERMINISTIC; INV-IMPORT-VALIDATES-HASHES
  Migration: legacy `bundle.container.json` remains a compatibility surface until LIB-6 export/import engines fully replace it

- Date: 2026-03-11
  Schema(s): schema/lib/provides_declaration.schema; schema/lib/provides_resolution.schema; schema/lib/instance_manifest.schema; schema/instance.manifest.schema; schema/packs/pack_lock.schema; schema/packs/pack_compat_manifest.schema; schema/pack_manifest.schema
  Change: add LIB-5 fork namespacing plus deterministic provides declarations and resolution records across instance and pack-lock contracts
  Invariants: INV-SCHEMA-VERSION-BUMP; INV-FORKS-MUST-NAMESPACE; INV-PROVIDES-RESOLUTION-DETERMINISTIC; INV-STRICT-REFUSES-AMBIGUITY
  Migration: legacy reverse-DNS pack ids remain loadable; normalize provider declarations and instance/lock resolution records through `lib/provides/provider_resolution.py`

- Date: 2026-03-11
  Schema(s): schema/lib/artifact_manifest.schema; schema/lib/artifact_reference.schema; schema/profile/profile_bundle.schema; schema/materials/blueprint.schema; schema/system/system_template.schema; schema/process/process_definition.schema
  Change: add LIB-4 shareable artifact manifest/reference contracts plus compatible payload envelope fields for profile bundles, blueprints, system templates, and process definitions
  Invariants: INV-SCHEMA-VERSION-BUMP; INV-SHAREABLE-ARTIFACTS-MUST-HAVE-MANIFEST; INV-ARTIFACTS-CONTENT-ADDRESSED; INV-ARTIFACT-LOAD-VALIDATED
  Migration: existing payload schemas remain loadable; LIB-4 export/store flows canonicalize the artifact envelope or sidecar through `lib/artifact/artifact_validator.py`

- Date: 2026-03-11
  Schema(s): schema/lib/save_manifest.schema; schema/lib/migration_event.schema; schema/save.manifest.schema
  Change: upgrade save manifest contracts for LIB-3 pinned contract bundles, explicit migration lineage, and read-only fallback policy
  Invariants: INV-SCHEMA-VERSION-BUMP; INV-SAVE-MANIFEST-REQUIRED; INV-SAVE-PINS-CONTRACTS; INV-NO-SILENT-MIGRATION
  Migration: normalize legacy save manifests through `lib/save/save_validator.py`; legacy adapter field `contract_bundle_hash` remains available for compatibility

- Date: 2026-03-11
  Schema(s): schema/lib/instance_manifest.schema; schema/lib/instance_settings.schema; schema/instance.manifest.schema
  Change: upgrade instance manifest contracts for LIB-2 instance kinds, save associations, portable embedded builds, and explicit pack/profile binding
  Invariants: INV-SCHEMA-VERSION-BUMP; INV-INSTANCE-USES-PACK-LOCK; INV-INSTANCE-USES-PROFILE-BUNDLE; INV-SAVES-NOT-EMBEDDED-IN-INSTANCE
  Migration: normalize legacy instance manifests through `lib/instance/instance_validator.py`; legacy adapter fields remain available for existing launcher/setup flows

- Date: 2026-03-11
  Schema(s): schema/lib/install_manifest.schema; schema/lib/product_build_descriptor.schema; schema/lib/instance_manifest.schema; schema/install.manifest.schema
  Change: upgrade install manifest contracts for LIB-1 multi-install build selection, per-product binary descriptors, and instance build pinning
  Invariants: INV-SCHEMA-VERSION-BUMP; INV-INSTALL-MANIFEST-REQUIRED; INV-INSTALL-NO-ABSOLUTE-PATH-DEPENDENCY; INV-BINARY-HASH-MATCHES-MANIFEST
  Migration: regenerate or explicitly refuse provisional LIB-0 install manifests; legacy install.manifest.json remains the compatibility adapter

- Date: 2026-03-11
  Schema(s): schema/lib/store_root.schema; schema/lib/install_manifest.schema; schema/lib/instance_manifest.schema; schema/lib/save_manifest.schema
  Change: add LIB-0 content-store root, install, instance, and save manifest contracts for CAS-backed linked/portable flows
  Invariants: INV-SCHEMA-VERSION-BUMP; INV-ARTIFACTS-CONTENT-ADDRESSED; INV-NO-PATH-BASED-SEMANTICS; INV-PORTABLE-MODE-SELF-CONTAINED
  Migration: none (new schemas; existing top-level install/instance/save schemas remain compatibility adapters)

- Date: 2026-02-07
  Schema(s): schema/pack_manifest.schema; schema/stage.declaration.schema
  Change: add explicit capability-stage metadata contract for pack manifests and stage declaration schema
  Invariants: INV-SCHEMA-VERSION-BUMP; INV-SCHEMA-NO-IMPLICIT-DEFAULTS; INV-SCHEMA-VERSION-REF
  Migration: none (pack_manifest minor bump; explicit stage fields required by RepoX/TestX governance)

- Date: 2026-02-02
  Schema(s): schema/identity/artifact_identity.schema
  Change: add artifact identity manifest contract for BUILD-ID-0 stage 1
  Invariants: INV-SCHEMA-VERSIONED; INV-SCHEMA-UNKNOWN-PRESERVE; INV-SCHEMA-NO-SEMANTIC-REUSE; INV-UNITS-ANNOTATED
  Migration: none (new schema)

- Date: 2026-02-08
  Schema(s): schema/SCHEMA_MIGRATION_REGISTRY.json
  Change: add machine-readable explicit migration route registry and deterministic route linkage
  Invariants: INV-SCHEMA-VERSION-BUMP; INV-SCHEMA-MIGRATION-ROUTES; INV-SCHEMA-NO-IMPLICIT-DEFAULTS; INV-SCHEMA-VERSION-REF
  Migration: none (governance metadata only)

- Date: 2026-02-01
  Schema(s): schema/ui/ui_node.schema; schema/ui/ui_layout.schema; schema/ui/ui_event.schema; schema/ui/ui_accessibility.schema; schema/ui/ui_string_key.schema
  Change: add UI IR schema primitives for binding validation and localization
  Invariants: INV-SCHEMA-VERSIONED; INV-SCHEMA-UNKNOWN-PRESERVE; INV-SCHEMA-NO-SEMANTIC-REUSE; INV-UNITS-ANNOTATED
  Migration: none (new schemas)

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
