Status: DERIVED
Last Reviewed: 2026-02-26
Supersedes: none
Superseded By: none

# Gate Remediation Record

- gate: `verify`
- blocker_type: `DERIVED_ARTIFACT_STALE`
- artifact_dir: `docs/audit/remediation/ws-426fb129fc29daec/20260226T070322Z_verify_DERIVED_ARTIFACT_STALE`

## Failure Output

```
WARN: WARN-GLOSSARY-TERM-CANON: docs/audit/remediation/vs2026/20260213T052649Z_precheck_DERIVED_ARTIFACT_STALE/failure.md uses forbidden synonym 'survival_mode' for ExperienceProfile
WARN: WARN-GLOSSARY-TERM-CANON: docs/audit/remediation/vs2026/20260213T063945Z_verify_DERIVED_ARTIFACT_STALE/failure.md uses forbidden synonym 'survival_mode' for ExperienceProfile
INV-AUDITX-ARTIFACT-HEADERS: forbidden run-meta key 'created_utc' in docs/audit/auditx/FINDINGS.json
INV-CANON-INDEX: architecture doc missing from CANON_INDEX: docs/architecture/astronomy_catalogs.md
INV-CANON-INDEX: architecture doc missing from CANON_INDEX: docs/architecture/camera_and_navigation.md
INV-CANON-INDEX: architecture doc missing from CANON_INDEX: docs/architecture/deterministic_packaging.md
INV-CANON-INDEX: architecture doc missing from CANON_INDEX: docs/architecture/fidelity_policy.md
INV-CANON-INDEX: architecture doc missing from CANON_INDEX: docs/architecture/hash_anchors.md
INV-CANON-INDEX: architecture doc missing from CANON_INDEX: docs/architecture/interest_regions.md
INV-CANON-INDEX: architecture doc missing from CANON_INDEX: docs/architecture/lens_system.md
INV-CANON-INDEX: architecture doc missing from CANON_INDEX: docs/architecture/macro_capsules.md
INV-CANON-INDEX: architecture doc missing from CANON_INDEX: docs/architecture/session_lifecycle.md
INV-CANON-INDEX: architecture doc missing from CANON_INDEX: docs/architecture/setup_and_launcher.md
INV-CANON-INDEX: architecture doc missing from CANON_INDEX: docs/architecture/site_registry.md
INV-CANON-INDEX: architecture doc missing from CANON_INDEX: docs/architecture/truth_perceived_render.md
INV-CANON-INDEX: architecture doc missing from CANON_INDEX: docs/architecture/ui_registry.md
INV-CANON-INDEX: canon index mismatch (expected CANONICAL): docs/architecture/BUDGET_POLICY.md
INV-CANON-INDEX: canonical doc not listed in CANON_INDEX: docs/scale/GALAXY_SCALE_READINESS.md
INV-CANON-INDEX: canonical doc not listed in CANON_INDEX: docs/worldgen/REAL_DATA_IMPORT_PIPELINE.md
INV-CANON-INDEX: canonical doc not listed in CANON_INDEX: docs/worldgen/WORLDGEN_CONSTRAINTS.md
INV-DERIVED-ARTIFACT-CONTRACT: canonical artifact 'artifact.auditx.findings' contains forbidden run-meta key 'created_utc'
INV-DOC-STATUS-HEADER: missing status header: docs/STATUS_NOW.md
INV-DOC-STATUS-HEADER: missing status header: docs/architecture/EXTENSION_MAP.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/AUDITX_BASELINE_REPORT.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/CAMERA_VIEW_BASELINE.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/CANON_CONFORMANCE_REPORT.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/CIVILISATION_SUBSTRATE_BASELINE.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/COHORT_REFINEMENT_BASELINE.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/CROSS_SYSTEM_CONSISTENCY_MATRIX.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/DETERMINISM_ENVELOPE_REPORT.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/DEVELOPER_ACCELERATION_BASELINE.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/DIEGETIC_FIRST_BASELINE.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/DIEGETIC_INSTRUMENTS_BASELINE.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/DOMAIN_REGISTRY_REPORT.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/EMBODIED_MOVEMENT_BASELINE.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/EPISTEMICS_OVER_NETWORK_BASELINE.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/EPISTEMIC_MEMORY_BASELINE.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/FAILURE_MODE_CATALOG.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/FINAL_SYSTEM_BASELINE.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/HANDSHAKE_COMPAT_MATRIX.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/LOD_EPISTEMIC_INVARIANCE_BASELINE.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/MULTIPLAYER_BASELINE_FINAL.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/MULTIPLAYER_CONTRACT_FOUNDATION_REPORT.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/MULTIPLAYER_DETERMINISM_ENVELOPE.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/MULTIPLAYER_SECURITY_BASELINE.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/NET_HANDSHAKE_COMPATIBILITY_REPORT.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/ORDER_LANGUAGE_BASELINE.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/RANKED_SERVER_GOVERNANCE_BASELINE.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/REAL_DATA_INTEGRATION_REPORT.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/RENDERMODEL_CONTRACT_BASELINE.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/REPRESENTATION_BASELINE.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/SERVER_AUTHORITATIVE_BASELINE_REPORT.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/SRZ_HYBRID_BASELINE_REPORT.md
INV-DOC-STATUS-HEADER: missing status header: docs/audit/WORLDGEN_CONSTRAINT_SOLVER_REPORT.md
INV-DOC-STATUS-HEADER: missing status header: docs/civilisation/COHORT_MODEL.md
INV-DOC-STATUS-HEADER: missing status header: docs/civilisation/DIPLOMACY_STUBS.md
INV-DOC-STATUS-HEADER: missing status header: docs/civilisation/FACTIONS_AND_AFFILIATION.md
INV-DOC-STATUS-HEADER: missing status header: docs/civilisation/INSTITUTIONS_AND_ROLES.md
INV-DOC-STATUS-HEADER: missing status header: docs/civilisation/ORDER_LANGUAGE.md
INV-DOC-STATUS-HEADER: missing status header: docs/civilisation/TERRITORY_AND_CLAIMS.md
INV-DOC-STATUS-HEADER: missing status header: docs/dev/DEVELOPER_ACCELERATION_MODEL.md
INV-DOC-STATUS-HEADER: missing status header: docs/dev/IMPACT_GRAPH.md
INV-DOC-STATUS-HEADER: missing status header: docs/diegetics/COMMUNICATION_CHANNELS_OVERVIEW.md
INV-DOC-STATUS-HEADER: missing status header: docs/diegetics/DIEGETIC_FIRST_ENFORCEMENT.md
INV-DOC-STATUS-HEADER: missing status header: docs/diegetics/DIEGETIC_INSTRUMENT_DOCTRINE.md
INV-DOC-STATUS-HEADER: missing status header: docs/diegetics/MAP_AND_NOTEBOOK_MODEL.md
INV-DOC-STATUS-HEADER: missing status header: docs/embodiment/CAMERA_AND_VIEW_LENSES.md
INV-DOC-STATUS-HEADER: missing status header: docs/embodiment/MOVEMENT_PROCESSES.md
INV-DOC-STATUS-HEADER: missing status header: docs/embodiment/REPRESENTATION_LAYER.md
INV-DOC-STATUS-HEADER: missing status header: docs/epistemics/LOD_EPISTEMIC_INVARIANCE.md
INV-DOC-STATUS-HEADER: missing status header: docs/epistemics/MEMORY_AND_FOG_OF_WAR.md
INV-DOC-STATUS-HEADER: missing status header: docs/net/ANTI_CHEAT_ENFORCEMENT_ACTIONS.md
INV-DOC-STATUS-HEADER: missing status header: docs/net/ANTI_CHEAT_MODULES.md
INV-DOC-STATUS-HEADER: missing status header: docs/net/ANTI_CHEAT_POLICY_FRAMEWORK.md
INV-DOC-STATUS-HEADER: missing status header: docs/net/DIEGETIC_CHANNELS_OVER_NETWORK.md
INV-DOC-STATUS-HEADER: missing status header: docs/net/EPISTEMICS_OVER_NETWORK.md
INV-DOC-STATUS-HEADER: missing status header: docs/net/EPISTEMIC_SCOPE_AND_FOG_OF_WAR.md
INV-DOC-STATUS-HEADER: missing status header: docs/net/ESPORTS_PROOF_ARTIFACTS.md
INV-DOC-STATUS-HEADER: missing status header: docs/net/HANDSHAKE_AND_COMPATIBILITY.md
INV-DOC-STATUS-HEADER: missing status header: docs/net/MULTIPLAYER_MODEL_OVERVIEW.md
INV-DOC-STATUS-HEADER: missing status header: docs/net/RANKED_SERVER_GOVERNANCE.md
INV-DOC-STATUS-HEADER: missing status header: docs/net/REPLICATION_POLICIES.md
INV-DOC-STATUS-HEADER: missing status header: docs/net/SERVER_AUTHORITATIVE_POLICY.md
INV-DOC-STATUS-HEADER: missing status header: docs/net/SRZ_HYBRID_POLICY.md
INV-DOC-STATUS-HEADER: missing status header: docs/net/TRANSPORT_ABSTRACTION.md
INV-DOC-STATUS-HEADER: missing status header: docs/render/PROCEDURAL_RENDERING_DEFAULTS.md
INV-DOC-STATUS-HEADER: missing status header: docs/render/RENDERMODEL_CONTRACT.md
INV-DOC-STATUS-HEADER: missing status header: docs/security/SECUREX_TRUST_MODEL.md
INV-IDENTITY-FINGERPRINT: stale identity fingerprint docs/audit/identity_fingerprint.json
INV-NO-RAW-PATHS: schema/net/server_policy_registry.schema:2: windows absolute path
INV-NO-RAW-PATHS: schema/worldgen/dem_source.schema:2: windows absolute path
INV-NO-RAW-PATHS: schema/worldgen/ephemeris_source.schema:2: windows absolute path
INV-NO-RAW-PATHS: schema/worldgen/worldgen_constraints.schema:2: windows absolute path
INV-NO-RAW-PATHS: schema/worldgen/worldgen_search_plan.schema:2: windows absolute path
INV-REPOX-RULESET-MISSING: rule_id not mapped to ruleset INV-AUDITX-PROMOTION-CANDIDATE-SHAPE
INV-REPOX-RULESET-MISSING: rule_id not mapped to ruleset INV-TOOL-UNRESOLVABLE
INV-REPOX-STRUCTURE: top-level directory not in REPO_INTENT: bundles
INV-REPOX-STRUCTURE: top-level directory not in REPO_INTENT: saves
INV-REPOX-STRUCTURE: top-level directory not in REPO_INTENT: src
INV-REPOX-STRUCTURE: top-level directory not in REPO_INTENT: worldgen
INV-TOOL-VERSION-MISMATCH: hash mismatch for tools/auditx/auditx.py (expected 4350ab3a056da7ae0b6b3d86166d5bb165d76ed8e40372e7447835f6a789407e, got 144b6dc8f67d81350e2cf88020af5341a623aa3cda17471dfa3afd2ef474930b)
INV-TOOL-VERSION-MISMATCH: hash mismatch for tools/compatx/compatx.py (expected 09c1dde3b93df65ba1df0fba2f184fbd80fe64e57e9bd9f7a68c980774659af1, got 7ce9387818e8070df8528015faacd1d36dadff9f52fbae0e99a687257a01c0d6)
INV-TOOL-VERSION-MISMATCH: hash mismatch for tools/controlx/controlx.py (expected 97e4890766339d131cfee5694b5429f368d9402a783c1c5621e6339d59a6aeb7, got 665d5d8f7359cd325e2dffe000945ba055af5816f6acc97c61d44341b67fe325)
INV-TOOL-VERSION-MISMATCH: hash mismatch for tools/securex/securex.py (expected 1c03332e38e70d462251be1db83e11f4ae7e4482f50484280347d5d075ee4da2, got e289f3f39a3f736785fad954153cbf70188ef4236684be3e4a046009e1fc93b7)
```
