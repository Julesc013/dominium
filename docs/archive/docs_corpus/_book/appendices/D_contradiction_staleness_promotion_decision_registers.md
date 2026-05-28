Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/`
Conversation Corpus Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

# Appendix D - Contradiction, Staleness, Promotion, and Decision Registers

The full registers are generated as Markdown reports under `_audit/` and `_reconciliation/`.

- Contradiction/drift findings: 136
- Staleness/verification candidates: 3303
- Promotion queue candidates: 484

## Sample Findings

| Finding ID | Class | Sources | Severity | Disposition |
| --- | --- | --- | --- | --- |
| DOC-CONTRA-0001 | archive_vs_current | docs/archive/audit/ARCH_AUDIT_CONSTITUTION.md | medium | quarantine_for_review |
| DOC-CONTRA-0002 | archive_vs_current | docs/archive/audit/ARTIFACT_MANIFEST_BASELINE.md | medium | quarantine_for_review |
| DOC-CONTRA-0003 | archive_vs_current | docs/archive/audit/FORKING_PROVIDES_BASELINE.md | medium | quarantine_for_review |
| DOC-CONTRA-0004 | archive_vs_current | docs/archive/audit/INSTALL_MANIFEST_BASELINE.md | medium | quarantine_for_review |
| DOC-CONTRA-0005 | archive_vs_current | docs/archive/audit/INSTANCE_MANIFEST_BASELINE.md | medium | quarantine_for_review |
| DOC-CONTRA-0006 | archive_vs_current | docs/archive/audit/INSTITUTIONAL_COMMS_BASELINE.md | medium | quarantine_for_review |
| DOC-CONTRA-0007 | archive_vs_current | docs/archive/audit/MACROCAPSULE_BEHAVIOR_BASELINE.md | medium | quarantine_for_review |
| DOC-CONTRA-0008 | archive_vs_current | docs/archive/audit/SAVE_MANIFEST_BASELINE.md | medium | quarantine_for_review |
| DOC-CONTRA-0009 | archive_vs_current | docs/archive/audit/SIG7_RETRO_AUDIT.md | medium | quarantine_for_review |
| DOC-CONTRA-0010 | archive_vs_current | docs/archive/audit/SUPERVISOR_HARDENING_FINAL.md | medium | quarantine_for_review |
| DOC-CONTRA-0011 | archive_vs_current | docs/archive/audit/SUPERVISOR_SURFACE_MAP.md | medium | quarantine_for_review |
| DOC-CONTRA-0012 | archive_vs_current | docs/archive/audit/SYSTEM_TIER_ROI_BASELINE.md | medium | quarantine_for_review |
| DOC-CONTRA-0013 | archive_vs_current | docs/archive/restructure/FUTURE_LAYOUT_PROPOSAL.md | medium | quarantine_for_review |
| DOC-CONTRA-0014 | archive_vs_current | docs/archive/restructure/RESTRUCTURE_RISKS.md | medium | quarantine_for_review |
| DOC-CONTRA-0015 | archive_vs_current | docs/archive/restructure/SHIM_POLICY.md | medium | quarantine_for_review |
| DOC-CONTRA-0016 | duplicate_shadow | docs/repo/repox/APRX_INTEGRATION_HOOKS.md, docs/archive/repox/APRX_INTEGRATION_HOOKS.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0017 | duplicate_shadow | docs/architecture/ARCHITECTURE.md, docs/archive/conversations/_wiki/topics/architecture.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0018 | duplicate_shadow | docs/testing/ci/CI_ENFORCEMENT_MATRIX.md, docs/archive/stray_root_docs/CI_ENFORCEMENT_MATRIX.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0019 | duplicate_shadow | docs/reference/specs/CIV0_POPULATION_GENESIS.md, docs/archive/stray_root_docs/CIV0_POPULATION_GENESIS.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0020 | duplicate_shadow | docs/reference/specs/CIV0a_SURVIVAL_LOOP.md, docs/archive/stray_root_docs/CIV0a_SURVIVAL_LOOP.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0021 | duplicate_shadow | docs/reference/specs/CIV1_CITIES_INFRA.md, docs/archive/stray_root_docs/CIV1_CITIES_INFRA.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0022 | duplicate_shadow | docs/reference/specs/CIV2_GOVERNANCE.md, docs/archive/stray_root_docs/CIV2_GOVERNANCE.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0023 | duplicate_shadow | docs/reference/specs/CIV3_KNOWLEDGE_TECH.md, docs/archive/stray_root_docs/CIV3_KNOWLEDGE_TECH.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0024 | duplicate_shadow | docs/reference/specs/CIV4_SCALE_AND_LOGISTICS.md, docs/archive/stray_root_docs/CIV4_SCALE_AND_LOGISTICS.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0025 | duplicate_shadow | docs/development/CONTRIBUTING.md, docs/archive/stray_root_docs/CONTRIBUTING.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0026 | duplicate_shadow | docs/testing/ci/DETERMINISM_TEST_MATRIX.md, docs/archive/stray_root_docs/DETERMINISM_TEST_MATRIX.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0027 | duplicate_shadow | docs/architecture/INVARIANTS.md, docs/archive/architecture/INVARIANTS.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0028 | duplicate_shadow | docs/development/guides/OFFLINE_AND_LOCAL_MP.md, docs/archive/stray_root_docs/OFFLINE_AND_LOCAL_MP.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0029 | duplicate_shadow | docs/governance/policies/PERF_BUDGETS.md, docs/archive/stray_root_docs/PERF_BUDGETS.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0030 | duplicate_shadow | docs/release/mvp/PRODUCT_BOOT_MATRIX.md, docs/archive/audit/convergence_steps/product_boot_matrix.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0031 | duplicate_shadow | docs/README.md, docs/archive/README.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0032 | duplicate_shadow | docs/reference/schema/SCHEMA_CANON_ALIGNMENT.md, docs/archive/audit/SCHEMA_CANON_ALIGNMENT.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0033 | duplicate_shadow | docs/governance/policies/VALIDATION_AND_GOVERNANCE.md, docs/archive/stray_root_docs/VALIDATION_AND_GOVERNANCE.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0034 | duplicate_shadow | docs/audit/VALIDATION_INVENTORY.md, docs/archive/audit/VALIDATION_INVENTORY.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0035 | duplicate_shadow | docs/audit/VALIDATION_REPORT_FAST.md, docs/archive/audit/VALIDATION_REPORT_FAST.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0036 | duplicate_shadow | docs/audit/VALIDATION_UNIFY_FINAL.md, docs/archive/audit/VALIDATION_UNIFY_FINAL.md | low | review_shadow_before_promotion |
| DOC-CONTRA-0037 | unclear_same_tier_conflict | docs/archive/audit/ULTRA_REPO_AUDIT_BUILD_RUN_TEST_MATRIX.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0038 | unclear_same_tier_conflict | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__00_manifest.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0039 | unclear_same_tier_conflict | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0040 | unclear_same_tier_conflict | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__02_context_transfer_packet.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0041 | unclear_same_tier_conflict | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__04_registers.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0042 | unclear_same_tier_conflict | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__05_aggregator_packet.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0043 | unclear_same_tier_conflict | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0044 | unclear_same_tier_conflict | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0045 | unclear_same_tier_conflict | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__08_future_chat_bootstrap_prompt.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0046 | unclear_same_tier_conflict | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0047 | unclear_same_tier_conflict | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0048 | unclear_same_tier_conflict | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__11_bundle_integrity_check.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0049 | unclear_same_tier_conflict | docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0050 | unclear_same_tier_conflict | docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__03_aggregator_packet.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0051 | unclear_same_tier_conflict | docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__04_registers.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0052 | unclear_same_tier_conflict | docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0053 | unclear_same_tier_conflict | docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0054 | unclear_same_tier_conflict | docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__manifest.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0055 | unclear_same_tier_conflict | docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0056 | unclear_same_tier_conflict | docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__03_aggregator_packet.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0057 | unclear_same_tier_conflict | docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__04_registers.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0058 | unclear_same_tier_conflict | docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0059 | unclear_same_tier_conflict | docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md | low | candidate_for_docs_hygiene_review |
| DOC-CONTRA-0060 | unclear_same_tier_conflict | docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__manifest.md | low | candidate_for_docs_hygiene_review |
| ... | ... | ... | ... | ... |
