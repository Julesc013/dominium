# POST-CONVERGE-10J Blockers

## Blocking Issues

Focused tuple `inv_repox_rules` still fails after authority-doc remediation with 60 failures and 5 warnings.

## Remaining Families

- `INV-NEW-CONTRACT-REQUIRES-ENTRY`: 9 (contract_registry_acceptance_backlog)
- `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR`: 7 (distribution_descriptor_product_proof_blocker)
- `INV-NO-ADHOC-MAIN`: 5 (distribution_descriptor_product_proof_blocker)
- `INV-TOOLS-REQUIRE-ENTITLEMENT`: 5 (retired_domain_path_policy_check)
- `INV-REPLAY-REFUSES-CONTRACT-MISMATCH`: 4 (remaining_repo_policy_blocker)
- `INV-CACHE-KEY-INCLUDES-CONTRACTS`: 2 (retired_domain_path_policy_check)
- `INV-TOOL-VERSION-MISMATCH`: 2 (tool_hash_audit_staleness)
- `INV-UNIVERSE-MUST-HAVE-CONTRACT-BUNDLE`: 2 (retired_domain_path_policy_check)
- `INV-BODY-MOTION-PROCESS-ONLY`: 1 (retired_domain_path_policy_check)
- `INV-CAMERA-SMOOTH-RENDER-ONLY`: 1 (retired_domain_path_policy_check)
- `INV-CANON-NO-SUPERSEDED`: 1 (remaining_repo_policy_blocker)
- `INV-COLLISION-DETERMINISTIC`: 1 (retired_domain_path_policy_check)
- `INV-CONFLICTS-NOT-SILENT-IN-STRICT`: 1 (retired_domain_path_policy_check)
- `INV-IDENTITY-FINGERPRINT`: 1 (tool_hash_audit_staleness)
- `INV-JUMP-PROFILE-GATED`: 1 (retired_domain_path_policy_check)
- `INV-LENS-PROFILED`: 1 (retired_domain_path_policy_check)
- `INV-LOCKLIST-FROZEN`: 1 (canon_index_local_acceptance)
- `INV-NO-ASSET-DEPENDENCY-FOR-EMB`: 1 (retired_domain_path_policy_check)
- `INV-NO-BLOCKING-WORLDGEN-IN-UI`: 1 (retired_domain_path_policy_check)
- `INV-NO-EXTENSION-INTERPRETATION-WITHOUT-REGISTRY`: 1 (remaining_repo_policy_blocker)
- `INV-NO-FLOAT-SMOOTHING`: 1 (retired_domain_path_policy_check)
- `INV-NO-IDENTITY-OVERRIDE`: 1 (retired_domain_path_policy_check)
- `INV-NO-RANDOM-RETRY-LOOPS-IN-WORLDGEN`: 1 (remaining_repo_policy_blocker)
- `INV-NO-SILENT-DEGRADE`: 1 (retired_domain_path_policy_check)
- `INV-NO-TRUTH-LEAK-IN-SCANS`: 1 (retired_domain_path_policy_check)
- `INV-OVERLAY-CONFLICT-POLICY-DECLARED`: 1 (retired_domain_path_policy_check)
- `INV-REFINEMENT-BUDGETED`: 1 (retired_domain_path_policy_check)
- `INV-REPOX-RULESET-MISSING`: 1 (remaining_repo_policy_blocker)
- `INV-REPRO-BUNDLE-DETERMINISTIC`: 1 (retired_domain_path_policy_check)
- `INV-REPRO-BUNDLE-NO-SECRETS`: 1 (retired_domain_path_policy_check)
- `INV-SHADOW-BOUNDED`: 1 (remaining_repo_policy_blocker)
- `INV-TERRAIN-EDITS-PROCESS-ONLY`: 1 (retired_domain_path_policy_check)

## Non-Blocking / Known Warnings

- INV-AUDITX-OUTPUT-STALE: audit outputs may be stale (190 commits since docs/audit/auditx/FINDINGS.json)
- WARN-GLOSSARY-TERM-CANON: docs/audit/auditx/FINDINGS.md uses forbidden synonym 'survival_mode' for ExperienceProfile
- WARN-GLOSSARY-TERM-CANON: docs/audit/remediation/vs2026/20260213T052649Z_precheck_DERIVED_ARTIFACT_STALE/failure.md uses forbidden synonym 'survival_mode' for ExperienceProfile
- WARN-GLOSSARY-TERM-CANON: docs/audit/remediation/vs2026/20260213T063945Z_verify_DERIVED_ARTIFACT_STALE/failure.md uses forbidden synonym 'survival_mode' for ExperienceProfile
- WARN-GLOSSARY-TERM-CANON: docs/audit/remediation/ws-426fb129fc29daec/20260226T070322Z_verify_DERIVED_ARTIFACT_STALE/failure.md uses forbidden synonym 'survival_mode' for ExperienceProfile

## Deferred Risks

- `INV-LOCKLIST-FROZEN` appears because this task changed `docs/architecture/CANON_INDEX.md` against local `origin/main`, matching the previously documented 10H canon-index update pattern.
- Full CTest was not run because focused RepoX remains a semantic blocker.
- Product boot proof remains blocked.

## Authorization

No root moves, deletes, renames, aliases, move maps, salvage maps, exception retirements, product boot proof, package proof, or release proof are authorized by this task.
