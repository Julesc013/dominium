# POST-CONVERGE-10G RepoX Failure Families

Status: PARTIAL

## Summary

POST-CONVERGE-10G reduced focused RepoX from 1844 failures and 5 warnings to 1769 failures and 5 warnings. The safe fixes address stale root/AppShell path assumptions and stale RepoX group-cache dependency behavior. Remaining failures are broad canonical documentation, contract acceptance, distribution descriptor, and retired-domain policy backlogs.

## Families

| Family | Classification | Before | After | Safe now? | Action | Notes |
| --- | --- | ---: | ---: | --- | --- | --- |
| `safe_stale_root_and_appshell_paths` | stale_path | 75 | 0 | true | fix_now | RepoX now uses runtime/appshell for AppShell source checks and consumes the current root allowlist plus active layout exceptions for top-level structure checks. |
| `repox_rule_cache_dependency` | stale_canonical_evidence | 0 | 0 | true | fix_now | The rule implementation path is now included in every group cache dependency hash. |
| `doc_status_header_backlog` | stale_canonical_evidence | 1545 | 1545 | false | defer | Classified as broad documentation status migration, not safe to mass-edit under 10G. |
| `canon_index_backlog` | missing_canonical_acceptance | 84 | 84 | false | needs_generator | Classified as canonical-index migration work requiring a source-of-truth review or generator path. |
| `historical_reference_backlog` | duplicate_cascade | 81 | 81 | false | defer | Preserved as historical/generated-reference debt pending a quarantine/archive policy task. |
| `contract_registry_acceptance_backlog` | missing_canonical_acceptance | 9 | 9 | false | document_blocker | Deferred because adding semantic contract entries is authority-sensitive. |
| `distribution_descriptor_backlog` | real_policy_violation | 12 | 12 | false | document_blocker | Kept blocking; product/distribution proof is outside 10G. |
| `retired_domain_path_backlog` | stale_path | None | 23 | false | defer | Classified but not remapped broadly; requires domain-owner path review. |
| `tool_hash_and_audit_staleness` | stale_canonical_evidence | None | 3 | false | needs_generator | Deferred until a tool-version/audit-output refresh task can identify the canonical generator and acceptance rule. |
| `other_policy_backlog` | real_policy_violation | None | 31 | false | document_blocker | Kept blocking until a narrower owner-specific remediation task can prove each rule family. |

## Remaining Failure Counts

| Invariant | Count | Example |
| --- | ---: | --- |
| `INV-DOC-STATUS-HEADER` | 1545 | INV-DOC-STATUS-HEADER: invalid status 'PROVISIONAL' in docs/repo/audits/CONVERGE_00_BASELINE.md |
| `INV-CANON-INDEX` | 84 | INV-CANON-INDEX: canonical doc not listed in CANON_INDEX: docs/agents/AGENT_MIRROR_POLICY.md |
| `INV-CANON-NO-HIST-REF` | 81 | INV-CANON-NO-HIST-REF: archived doc referenced by docs/refactor/QUARANTINE_duplicate.cluster.0a8e71d06f3c5f95.md |
| `INV-NEW-CONTRACT-REQUIRES-ENTRY` | 9 | INV-NEW-CONTRACT-REQUIRES-ENTRY: semantic contract token missing registry entry contract.arch.graph.v1 (data/architecture/architecture_graph.v1.json) |
| `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR` | 7 | INV-ALL-PRODUCTS-EMIT-DESCRIPTOR: missing archive/generated/dist/bin/client |
| `INV-NO-ADHOC-MAIN` | 5 | INV-NO-ADHOC-MAIN: missing archive/generated/dist/bin/engine |
| `INV-TOOLS-REQUIRE-ENTITLEMENT` | 5 | INV-TOOLS-REQUIRE-ENTITLEMENT: missing embodiment/tools/logic_tool.py |
| `INV-REPLAY-REFUSES-CONTRACT-MISMATCH` | 4 | INV-REPLAY-REFUSES-CONTRACT-MISMATCH: universe\universe_contract_enforcer.py missing token Replay requires SessionSpec.semantic_contract_registry_hash |
| `INV-CACHE-KEY-INCLUDES-CONTRACTS` | 2 | INV-CACHE-KEY-INCLUDES-CONTRACTS: missing geo/worldgen/worldgen_engine.py |
| `INV-TOOL-VERSION-MISMATCH` | 2 | INV-TOOL-VERSION-MISMATCH: hash mismatch for tools/xstack/compatx/compatx.py (expected 14038782c57cde4ba0b1645fefa3b6b23d3d488a60201fa66d39c6470d503d1a, got 684fce553b870fea424c8a49f85f41958a61f5512ee0965186e50c210b934b6c) |
| `INV-UNIVERSE-MUST-HAVE-CONTRACT-BUNDLE` | 2 | INV-UNIVERSE-MUST-HAVE-CONTRACT-BUNDLE: missing universe\universe_contract_enforcer.py |
| `INV-BODY-MOTION-PROCESS-ONLY` | 1 | INV-BODY-MOTION-PROCESS-ONLY: missing embodiment/body/body_system.py |
| `INV-CAMERA-SMOOTH-RENDER-ONLY` | 1 | INV-CAMERA-SMOOTH-RENDER-ONLY: missing embodiment/lens/camera_smoothing.py |
| `INV-CANON-NO-SUPERSEDED` | 1 | INV-CANON-NO-SUPERSEDED: canonical doc marked superseded: docs/architecture/DIRECTORY_CONTEXT.md |
| `INV-COLLISION-DETERMINISTIC` | 1 | INV-COLLISION-DETERMINISTIC: missing embodiment/collision/macro_heightfield_provider.py |
| `INV-CONFLICTS-NOT-SILENT-IN-STRICT` | 1 | INV-CONFLICTS-NOT-SILENT-IN-STRICT: missing geo/overlay/overlay_merge_engine.py |
| `INV-IDENTITY-FINGERPRINT` | 1 | INV-IDENTITY-FINGERPRINT: stale identity fingerprint docs/audit/identity_fingerprint.json |
| `INV-JUMP-PROFILE-GATED` | 1 | INV-JUMP-PROFILE-GATED: missing embodiment/movement/jump_process.py |
| `INV-LENS-PROFILED` | 1 | INV-LENS-PROFILED: missing embodiment/lens/lens_engine.py |
| `INV-NO-ASSET-DEPENDENCY-FOR-EMB` | 1 | INV-NO-ASSET-DEPENDENCY-FOR-EMB: missing embodiment/body/body_system.py |

## Warning Counts

| Warning | Count | Example |
| --- | ---: | --- |
| `WARN-GLOSSARY-TERM-CANON` | 4 | WARN-GLOSSARY-TERM-CANON: docs/audit/auditx/FINDINGS.md uses forbidden synonym 'survival_mode' for ExperienceProfile |
| `INV-AUDITX-OUTPUT-STALE` | 1 | INV-AUDITX-OUTPUT-STALE: audit outputs may be stale (185 commits since docs/audit/auditx/FINDINGS.json) |
