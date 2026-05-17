# MOVE-BULK-08 Closure Validation

Generated: 2026-05-17T15:45:20Z

## Results

| Check | Result | Exit |
| --- | --- | ---: |
| AIDE doctor | FAIL | 1 |
| AIDE validate | FAIL | 1 |
| AIDE test | PASS | 0 |
| AIDE selftest | PASS | 0 |
| AIDE tools validate | PASS | 0 |
| AIDE roots validate | PASS | 0 |
| AIDE repo validate | PASS | 0 |
| AIDE commit check latest | PASS | 0 |
| closure JSON parse | PASS | 0 |
| strict repo layout | PASS | 0 |
| strict root allowlist | PASS | 0 |
| strict distribution layout | PASS | 0 |
| strict component matrices | PASS | 0 |
| docs sanity | PASS | 0 |
| build target boundaries | PASS | 0 |
| UI shell purity | PASS | 0 |
| ABI boundaries | PASS | 0 |
| focused RepoX | FAIL | 8 |
| git status | PASS | 0 |
| git diff check | PASS | 0 |
| git diff cached check | PASS | 0 |
| ignored local status | PASS | 0 |

## Command Output Snippets

### AIDE doctor - FAIL

```text
AIDE Lite doctor
status: FAIL
- repo_root: C:/Inbox/Git Repos/dominium
- PASS required: .aide/policies/token-budget.yaml
- PASS required: .aide/memory/project-state.md
- PASS required: .aide/memory/decisions.md
- PASS required: .aide/memory/open-risks.md
- PASS required: .aide/prompts/compact-task.md
- PASS required: .aide/prompts/evidence-review.md
- PASS required: .aide/prompts/codex-token-mode.md
- PASS required: .aide/context/ignore.yaml
- INFO Q09 status: missing
- INFO Q10 status: missing
- INFO Q11 status: missing
- INFO Q12 status: missing
- INFO Q13 status: missing
- INFO Q14 status: missing
- INFO Q15 status: missing
- INFO Q16 status: missing
- INFO Q17 status: missing
- INFO Q18 status: missing
- INFO Q19 status: missing
- INFO Q20 status: missing
- PASS snapshot exists: .aide/context/repo-snapshot.json
- PASS latest task packet exists: .aide/context/latest-task-packet.md
- PASS context artifact exists: .aide/context/repo-map.json
- PASS context artifact exists: .aide/context/repo-map.md
- PASS context artifact exists: .aide/context/test-map.json
- PASS context artifact exists: .aide/context/context-index.json
- PASS context artifact exists: .aide/context/latest-context-packet.md
- PASS verifier artifact exists: .aide/policies/verification.yaml
- PASS verifier artifact exists: .aide/verification/latest-verification-report.md
- PASS review artifact exists: .aide/verification/review-decision-policy.yaml
- PASS review artifact exists: .aide/context/latest-review-packet.md
- PASS token ledger artifact exists: .aide/policies/token-ledger.yaml
- PASS token ledger artifact exists: .aide/reports/token-baselines.yaml
- PASS token ledger artifact exists: .aide/reports/token-ledger.jsonl
- PASS token ledger artifact exists: .aide/reports/token-savings-summary.md
- PASS token ledger records: 16
- PASS golden task artifact exists: .aide/policies/evals.yaml
- PASS golden task artifact exists: .aide/evals/golden-tasks/README.md
- PASS golden task artifact exists: .aide/evals/golden-tasks/catalog.yaml
- PASS golden task definitions: 130
- PASS golden task report exists: .aide/evals/runs/latest-golden-tasks.json
- PASS golden task report exists: .aide/evals/runs/latest-golden-tasks.md
- PASS controller artifact exists: .aide/policies/controller.yaml
- PASS controller artifact exists: .aide/controller/README.md
- PASS controller artifact exists: .aide/controller/outcome-ledger.jsonl
- PASS controller artifact exists: .aide/controller/latest-outcome-report.md
- PASS controller artifact exists: .aide/controller/latest-recommendations.md
- PASS controller artifact exists: .aide/controller/failure-taxonomy.yaml
- PASS outcome ledger records: 7
- PASS routing artifact exists: .aide/policies/routing.yaml
- PASS routing artifact exists: .aide/models/README.md
- PASS routing artifact exists: .aide/models/providers.yaml
- PASS routing artifact exists: .aide/models/capabilities.yaml
- PASS routing artifact exists: .aide/models/routes.yaml
- PASS routing artifact
... truncated ...
```

### AIDE validate - FAIL

```text
AIDE Lite validate
status: FAIL
- PASS required file: .aide/policies/token-budget.yaml
- PASS required file: .aide/memory/project-state.md
- PASS required file: .aide/memory/decisions.md
- PASS required file: .aide/memory/open-risks.md
- PASS required file: .aide/prompts/compact-task.md
- PASS required file: .aide/prompts/evidence-review.md
- PASS required file: .aide/prompts/codex-token-mode.md
- PASS required file: .aide/context/ignore.yaml
- PASS context compiler config exists: .aide/context/compiler.yaml
- PASS context compiler config exists: .aide/context/priority.yaml
- PASS context compiler config exists: .aide/context/excerpt-policy.yaml
- PASS verifier config exists: .aide/policies/verification.yaml
- PASS verifier config exists: .aide/verification/evidence-packet.template.md
- PASS verifier config exists: .aide/verification/review-packet.template.md
- PASS verifier config exists: .aide/verification/review-decision-policy.yaml
- PASS verifier config exists: .aide/verification/diff-scope-policy.yaml
- PASS verifier config exists: .aide/verification/file-reference-policy.yaml
- PASS verifier config exists: .aide/verification/secret-scan-policy.yaml
- PASS XStack contract schema version is v0
- PASS XStack wrapper registry schema version is v0
- PASS XStack contract enforces no_apply true
- PASS XStack contract enforces execution_allowed false
- PASS XStack contract enforces apply_allowed false
- PASS XStack registry enforces no_apply true
- PASS XStack registry enforces execution_allowed false
- PASS XStack registry enforces apply_allowed false
- PASS XStack registry models XStack/AuditX/RepoX/TestX families
- PASS XStack registry contains wrapper plans for modeled systems
- PASS XStack registry detected xstack
- PASS XStack registry detected auditx
- PASS XStack registry detected repox
- PASS XStack registry detected testx
- PASS dominium.xstack.status execution_allowed false
- PASS dominium.xstack.status apply_allowed false
- PASS dominium.xstack.status no_apply true
- PASS dominium.auditx.status execution_allowed false
- PASS dominium.auditx.status apply_allowed false
- PASS dominium.auditx.status no_apply true
- PASS dominium.repox.policy execution_allowed false
- PASS dominium.repox.policy apply_allowed false
- PASS dominium.repox.policy no_apply true
- PASS dominium.testx.status execution_allowed false
- PASS dominium.testx.status apply_allowed false
- PASS dominium.testx.status no_apply true
- PASS dominium.buildx.status execution_allowed false
- PASS dominium.buildx.status apply_allowed false
- PASS dominium.buildx.status no_apply true
- PASS dominium.validation.profiles execution_allowed false
- PASS dominium.validation.profiles apply_allowed false
- PASS dominium.validation.profiles no_apply true
- PASS XStack integration excludes forbidden phrase: "execution_allowed": true
- PASS XStack integration excludes forbidden phrase: "apply_allowed": true
- PASS XStack integration excludes forbidden phrase: safe_to_delete
- PASS XStack i
... truncated ...
```

### AIDE test - PASS

```text
AIDE Lite test
status: PASS
- PASS internal estimate, ignore, snapshot, index, context, pack, adapt, drift, line-ref, verifier, review-pack, ledger, eval, commit, changelog, GitHub advisory, task, git workflow, intent, repo intelligence, quality, refactor, roots, tools, install, repair, upgrade, rollback, uninstall, outcome, optimize, route, cache, gateway, provider, adapter, and validate checks
```

### AIDE selftest - PASS

```text
AIDE Lite selftest
status: PASS
- PASS internal estimate, ignore, snapshot, index, context, pack, adapt, drift, line-ref, verifier, review-pack, ledger, eval, commit, changelog, GitHub advisory, task, git workflow, intent, repo intelligence, quality, refactor, roots, tools, install, repair, upgrade, rollback, uninstall, outcome, optimize, route, cache, gateway, provider, adapter, and validate checks
```

### AIDE tools validate - PASS

```text
AIDE Lite tools validate
result: PASS
- PASS Q41 required file exists: .aide/policies/tool-absorption.yaml
- PASS Q41 required file exists: .aide/policies/tool-inventory.yaml
- PASS Q41 required file exists: .aide/policies/tool-fates.yaml
- PASS Q41 required file exists: .aide/policies/tool-wrapping.yaml
- PASS Q41 required file exists: .aide/policies/tool-risk.yaml
- PASS Q41 required file exists: .aide/policies/tool-capabilities.yaml
- PASS Q41 required file exists: .aide/tools/tool-inventory.schema.json
- PASS Q41 required file exists: .aide/tools/tool-record.schema.json
- PASS Q41 required file exists: .aide/tools/tool-capability.schema.json
- PASS Q41 required file exists: .aide/tools/tool-wrap-plan.schema.json
- PASS Q41 required file exists: .aide/tools/tool-adapter-map.schema.json
- PASS Q41 required file exists: .aide/tools/tool-risk.schema.json
- PASS Q41 required file exists: .aide/tools/tool-retirement.schema.json
- PASS Q41 required file exists: .aide/tools/tool-evidence.schema.json
- PASS Q41 required file exists: .aide/tools/README.md
- PASS .aide/policies/tool-absorption.yaml contains anchor: aide.tool-absorption-policy.v0
- PASS .aide/policies/tool-absorption.yaml contains anchor: no_unknown_tool_execution
- PASS .aide/policies/tool-absorption.yaml contains anchor: drop_candidate_is_delete_approval: false
- PASS .aide/policies/tool-inventory.yaml contains anchor: aide.tool-inventory-policy.v0
- PASS .aide/policies/tool-inventory.yaml contains anchor: git_tracked_files
- PASS .aide/policies/tool-inventory.yaml contains anchor: execute_discovered_tools: false
- PASS .aide/policies/tool-fates.yaml contains anchor: aide.tool-fates-policy.v0
- PASS .aide/policies/tool-fates.yaml contains anchor: drop_candidate_is_not_deletion_approval: true
- PASS .aide/policies/tool-fates.yaml contains anchor: wrap_is_plan_not_execution: true
- PASS .aide/policies/tool-wrapping.yaml contains anchor: aide.tool-wrapping-policy.v0
- PASS .aide/policies/tool-wrapping.yaml contains anchor: execution_allowed: false
- PASS .aide/policies/tool-wrapping.yaml contains anchor: command_preview_is_documentation_only: true
- PASS .aide/policies/tool-risk.yaml contains anchor: aide.tool-risk-policy.v0
- PASS .aide/policies/tool-risk.yaml contains anchor: unknown_tool_execution_allowed: false
- PASS .aide/policies/tool-risk.yaml contains anchor: target_mutation_allowed_in_q41: false
- PASS .aide/policies/tool-capabilities.yaml contains anchor: aide.tool-capabilities-policy.v0
- PASS .aide/policies/tool-capabilities.yaml contains anchor: capability_mapping_is_advisory: true
- PASS .aide/policies/tool-capabilities.yaml contains anchor: no_wrapper_execution_from_mapping: true
- PASS .aide/tools/tool-inventory.schema.json is object schema
- PASS .aide/tools/tool-inventory.schema.json defines required fields
- PASS .aide/tools/tool-record.schema.json is object schema
- PASS .aide/tools/tool-record.schema.json defines required fields
- PASS .aide/tools/tool-capability.sch
... truncated ...
```

### AIDE roots validate - PASS

```text
AIDE Lite roots validate
result: PASS
- PASS Q40 required file exists: .aide/policies/root-recycling.yaml
- PASS Q40 required file exists: .aide/policies/root-inventory.yaml
- PASS Q40 required file exists: .aide/policies/root-fates.yaml
- PASS Q40 required file exists: .aide/policies/root-exceptions.yaml
- PASS Q40 required file exists: .aide/policies/root-risk.yaml
- PASS Q40 required file exists: .aide/refactors/root-inventory.schema.json
- PASS Q40 required file exists: .aide/refactors/root-record.schema.json
- PASS Q40 required file exists: .aide/refactors/root-file-classification.schema.json
- PASS Q40 required file exists: .aide/refactors/root-recycling-plan.schema.json
- PASS Q40 required file exists: .aide/refactors/root-exception.schema.json
- PASS Q40 required file exists: .aide/refactors/root-retirement.schema.json
- PASS Q40 required file exists: .aide/refactors/root-risk.schema.json
- PASS Q40 required file exists: .aide/roots/README.md
- PASS .aide/policies/root-recycling.yaml contains anchor: aide.root-recycling-policy.v0
- PASS .aide/policies/root-recycling.yaml contains anchor: deterministic_local
- PASS .aide/policies/root-recycling.yaml contains anchor: no_apply_in_q40
- PASS .aide/policies/root-recycling.yaml contains anchor: drop_candidate_is_deletion_approval: false
- PASS .aide/policies/root-inventory.yaml contains anchor: aide.root-inventory-policy.v0
- PASS .aide/policies/root-inventory.yaml contains anchor: git_tracked_files
- PASS .aide/policies/root-inventory.yaml contains anchor: top_level_directory_listing
- PASS .aide/policies/root-fates.yaml contains anchor: aide.root-fates-policy.v0
- PASS .aide/policies/root-fates.yaml contains anchor: drop_candidate_is_deletion_approval: false
- PASS .aide/policies/root-fates.yaml contains anchor: drop_candidate_is_not_safe_to_delete: true
- PASS .aide/policies/root-exceptions.yaml contains anchor: aide.root-exceptions-policy.v0
- PASS .aide/policies/root-exceptions.yaml contains anchor: retirement_condition_required: true
- PASS .aide/policies/root-exceptions.yaml contains anchor: exception_does_not_authorize_delete: true
- PASS .aide/policies/root-risk.yaml contains anchor: aide.root-risk-policy.v0
- PASS .aide/policies/root-risk.yaml contains anchor: tracked_local_or_secret_state_is_critical: true
- PASS .aide/policies/root-risk.yaml contains anchor: no_deletion_recommendation_from_risk: true
- PASS .aide/refactors/root-inventory.schema.json is object schema
- PASS .aide/refactors/root-inventory.schema.json defines required fields
- PASS .aide/refactors/root-record.schema.json is object schema
- PASS .aide/refactors/root-record.schema.json defines required fields
- PASS .aide/refactors/root-file-classification.schema.json is object schema
- PASS .aide/refactors/root-file-classification.schema.json defines required fields
- PASS .aide/refactors/root-recycling-plan.schema.json is object schema
- PASS .aide/refactors/root-recycling-plan.schema.json defines required fields
- PAS
... truncated ...
```

### AIDE repo validate - PASS

```text
AIDE Lite repo validate
result: PASS
- PASS Q37 required file exists: .aide/policies/repo-intelligence.yaml
- PASS Q37 required file exists: .aide/policies/file-classification.yaml
- PASS Q37 required file exists: .aide/policies/ownership-map.yaml
- PASS Q37 required file exists: .aide/policies/dependency-map.yaml
- PASS Q37 required file exists: .aide/policies/test-map.yaml
- PASS Q37 required file exists: .aide/policies/doc-link-map.yaml
- PASS Q37 required file exists: .aide/repo/file-inventory.schema.json
- PASS Q37 required file exists: .aide/repo/ownership-map.schema.json
- PASS Q37 required file exists: .aide/repo/dependency-map.schema.json
- PASS Q37 required file exists: .aide/repo/test-map.schema.json
- PASS Q37 required file exists: .aide/repo/doc-link-map.schema.json
- PASS Q37 required file exists: .aide/repo/repo-intelligence-summary.schema.json
- PASS Q37 required file exists: .aide/repo/README.md
- PASS Q37 required file exists: .aide/repo/file-inventory.json
- PASS Q37 required file exists: .aide/repo/ownership-map.json
- PASS Q37 required file exists: .aide/repo/dependency-map.json
- PASS Q37 required file exists: .aide/repo/test-map.json
- PASS Q37 required file exists: .aide/repo/doc-link-map.json
- PASS Q37 required file exists: .aide/repo/generated-map.json
- PASS Q37 required file exists: .aide/repo/orphan-candidates.json
- PASS Q37 required file exists: .aide/repo/latest-repo-intelligence.md
- PASS .aide/policies/repo-intelligence.yaml contains anchor: aide.repo-intelligence-policy.v0
- PASS .aide/policies/repo-intelligence.yaml contains anchor: deterministic_local
- PASS .aide/policies/repo-intelligence.yaml contains anchor: index_only
- PASS .aide/policies/repo-intelligence.yaml contains anchor: no_file_moves
- PASS .aide/policies/repo-intelligence.yaml contains anchor: no_file_deletes
- PASS .aide/policies/file-classification.yaml contains anchor: aide.file-classification-policy.v0
- PASS .aide/policies/file-classification.yaml contains anchor: source_extensions
- PASS .aide/policies/file-classification.yaml contains anchor: generated_or_evidence_paths
- PASS .aide/policies/file-classification.yaml contains anchor: exportable_hint_rules
- PASS .aide/policies/ownership-map.yaml contains anchor: aide.ownership-map-policy.v0
- PASS .aide/policies/ownership-map.yaml contains anchor: AIDE control plane
- PASS .aide/policies/ownership-map.yaml contains anchor: AIDE harness
- PASS .aide/policies/ownership-map.yaml contains anchor: unknown
- PASS .aide/policies/dependency-map.yaml contains anchor: aide.dependency-map-policy.v0
- PASS .aide/policies/dependency-map.yaml contains anchor: Python import
- PASS .aide/policies/dependency-map.yaml contains anchor: no code execution
- PASS .aide/policies/test-map.yaml contains anchor: aide.test-map-policy.v0
- PASS .aide/policies/test-map.yaml contains anchor: test_*.py
- PASS .aide/policies/test-map.yaml contains anchor: confidence
- PASS .aide/policies/doc-link-map.yaml contains ancho
... truncated ...
```

### AIDE commit check latest - PASS

```text
AIDE Lite commit check
result: PASS
source: git log -1 --pretty=%B
policy: .aide/policies/commit-messages.yaml
standard: .aide/reports/aide-commit-message-standard.md
- PASS commit subject is present
- PASS commit subject is 72 characters or fewer
- PASS commit subject follows type(scope): summary
- PASS commit type is allowed: audit
- PASS commit subject has no trailing period
- PASS commit subject is not a vague placeholder
- PASS commit summary is specific enough
- PASS commit body is present
- PASS blank line separates subject and Markdown body
- PASS commit body contains heading: ## Summary
- PASS commit body heading has content: ## Summary
- PASS commit body heading has bullet content: ## Summary
- PASS commit body contains heading: ## Why
- PASS commit body heading has content: ## Why
- PASS commit body heading has bullet content: ## Why
- PASS commit body contains heading: ## Changed
- PASS commit body heading has content: ## Changed
- PASS commit body heading has bullet content: ## Changed
- PASS commit body contains heading: ## Validation
- PASS commit body heading has content: ## Validation
- PASS commit body heading has bullet content: ## Validation
- PASS commit body contains heading: ## Changelog
- PASS commit body heading has content: ## Changelog
- PASS commit body heading has bullet content: ## Changelog
- PASS commit body contains heading: ## Risks
- PASS commit body heading has content: ## Risks
- PASS commit body heading has bullet content: ## Risks
- PASS commit body contains heading: ## Follow-up
- PASS commit body heading has content: ## Follow-up
- PASS commit body heading has bullet content: ## Follow-up
- PASS validation section records PASS/WARN/FAIL/NOT RUN outcome
- PASS changelog section uses a machine-readable category prefix
- PASS commit trailer present: AIDE-Task
- PASS commit trailer present: AIDE-Phase
- PASS commit trailer present: AIDE-Result
- PASS commit trailer present: AIDE-Scope
- PASS commit trailer present: AIDE-Token-Impact
- PASS commit trailer present: AIDE-Quality-Gate
- PASS commit message excludes raw_prompt_body
- PASS commit message excludes raw_response_body
- PASS commit message excludes begin private key
- PASS commit message excludes openai_api_key
- PASS commit message excludes anthropic_api_key
- PASS commit message excludes deepseek_api_key
- PASS commit message excludes sk-ant
```

### closure JSON parse - PASS

```text
parsed 4 closure json files
```

### strict repo layout - PASS

```text
Repo layout audit
contract_id: dominium.repo.layout.v1
contract_phase: CONVERGE-10
exception_contract_id: dominium.repo.layout_exceptions.v1
active_exception_count: 31
head_sha: 8534b644de09140ad8ee6d2db1c3eb44ac5b9b2d

Summary counts:
- allowed_file: 25
- canonical: 13
- generated_or_ephemeral: 2
- metadata: 4
- transitional_content_or_data_root: 7
- transitional_contract_or_schema_root: 8
- transitional_release_or_dist_root: 1
- transitional_runtime_root: 3
- unknown_needs_review: 9

Unknown/review roots:
- governance
- meta
- meta_extensions_engine.py
- numeric_discipline.py
- performance
- tool_ui_bind.cmd
- tool_ui_doc_annotate.cmd
- tool_ui_validate.cmd
- validation

Split-required roots:
- bundles
- compat
- control
- core
- data
- locks
- modding
- net
- packs
- repo
- safety
- security
- specs
- templates
- updates

Transitional aliases:
- bundles
- compat
- control
- core
- data
- lib
- libs
- locks
- modding
- models
- net
- packs
- profiles
- repo
- safety
- security
- specs
- templates
- updates

Generated roots:
- artifacts
- dist

Missing required canonical roots:
- external

Exceptions applied:
- missing_external_root: missing_required_canonical_root: external: missing required canonical root
- governance_root: unknown_or_violating_root: governance: unknown or violating root
- meta_root: unknown_or_violating_root: meta: unknown or violating root
- meta_extensions_engine_file: unknown_or_violating_root: meta_extensions_engine.py: unknown or violating root
- numeric_discipline_file: unknown_or_violating_root: numeric_discipline.py: unknown or violating root
- performance_root: unknown_or_violating_root: performance: unknown or violating root
- tool_ui_bind_cmd: unknown_or_violating_root: tool_ui_bind.cmd: unknown or violating root
- tool_ui_doc_annotate_cmd: unknown_or_violating_root: tool_ui_doc_annotate.cmd: unknown or violating root
- tool_ui_validate_cmd: unknown_or_violating_root: tool_ui_validate.cmd: unknown or violating root
- validation_root: unknown_or_violating_root: validation: unknown or violating root
- artifacts_root: generated_root_requires_exception: artifacts: generated root present
- bundles_root: transitional_root_requires_exception: bundles: transitional root present
- compat_root: transitional_root_requires_exception: compat: transitional root present
- control_root: transitional_root_requires_exception: control: transitional root present
- core_root: transitional_root_requires_exception: core: transitional root present
- data_root: transitional_root_requires_exception: data: transitional root present
- dist_root: generated_root_requires_exception: dist: generated root present
- lib_root: transitional_root_requires_exception: lib: transitional root present
- libs_root: transitional_root_requires_exception: libs: transitional root present
- locks_root: transitional_root_requires_exception: locks: transitional root present
- modding_root: transitional_root_requires_exception: modding: transitional root present
-
... truncated ...
```

### strict root allowlist - PASS

```text
Root allowlist audit
contract_id: dominium.repo.root_allowlist.v1
phase: CONVERGE-10
exception_contract_id: dominium.repo.layout_exceptions.v1
active_exception_count: 31
head_sha: 8534b644de09140ad8ee6d2db1c3eb44ac5b9b2d

Summary counts:
- allowed_file: 25
- canonical: 13
- generated_or_ephemeral: 2
- metadata: 4
- transitional: 23
- violation: 5

Unknown roots:
- meta_extensions_engine.py
- numeric_discipline.py
- tool_ui_bind.cmd
- tool_ui_doc_annotate.cmd
- tool_ui_validate.cmd

Transitional roots by retire phase:
- CONVERGE-02: governance
- CONVERGE-03: meta, performance, validation
- CONVERGE-06: lib, libs, repo, safety, security, specs, updates
- CONVERGE-07: control, core
- CONVERGE-09: bundles, data, modding, models, packs, profiles, templates
- review: compat, locks, net

Generated/ephemeral roots:
- artifacts
- dist

Missing expected canonical roots:
- none

Forbidden root patterns:
- new_domain_root
- new_product_root_outside_apps
- new_schema_root_outside_contracts
- new_runtime_adapter_root_outside_runtime
- generated_output_without_exception

Exceptions applied:
- meta_extensions_engine_file: unknown_or_violating_root_entry: meta_extensions_engine.py: unknown or violating root entry
- numeric_discipline_file: unknown_or_violating_root_entry: numeric_discipline.py: unknown or violating root entry
- tool_ui_bind_cmd: unknown_or_violating_root_entry: tool_ui_bind.cmd: unknown or violating root entry
- tool_ui_doc_annotate_cmd: unknown_or_violating_root_entry: tool_ui_doc_annotate.cmd: unknown or violating root entry
- tool_ui_validate_cmd: unknown_or_violating_root_entry: tool_ui_validate.cmd: unknown or violating root entry
- artifacts_root: generated_root_requires_exception: artifacts: generated root present
- bundles_root: transitional_root_requires_exception: bundles: transitional root present
- compat_root: transitional_root_requires_exception: compat: transitional root present
- control_root: transitional_root_requires_exception: control: transitional root present
- core_root: transitional_root_requires_exception: core: transitional root present
- data_root: transitional_root_requires_exception: data: transitional root present
- dist_root: generated_root_requires_exception: dist: generated root present
- governance_root: transitional_root_requires_exception: governance: transitional root present
- lib_root: transitional_root_requires_exception: lib: transitional root present
- libs_root: transitional_root_requires_exception: libs: transitional root present
- locks_root: transitional_root_requires_exception: locks: transitional root present
- meta_root: transitional_root_requires_exception: meta: transitional root present
- modding_root: transitional_root_requires_exception: modding: transitional root present
- models_root: transitional_root_requires_exception: models: transitional root present
- net_root: transitional_root_requires_exception: net: transitional root present
- packs_root: transitional_root_requires_exception: packs
... truncated ...
```

### strict distribution layout - PASS

```text
Distribution layout audit
contract_id: dominium.distribution.layout.v1
phase: CONVERGE-04
head_sha: 8534b644de09140ad8ee6d2db1c3eb44ac5b9b2d

Summary:
- logical_roots_declared: 20
- projections_declared: 11
- required_logical_roots: 20
- required_projections: 11
- warnings: 0

Missing logical roots:
- none

Missing projections:
- none

Warnings:
- none

Strict-mode result: pass
```

### strict component matrices - PASS

```text
Component matrix audit
contract_id: dominium.release.component_matrix.v1
phase: CONVERGE-11
head_sha: 8534b644de09140ad8ee6d2db1c3eb44ac5b9b2d

Summary:
- matrix_sections: 12
- support_tiers: 6
- warnings: 0

Matrix counts:
- audio_backends: 8
- distribution_projections: 11
- input_backends: 6
- native_shells: 7
- network_backends: 6
- packaging: 10
- platform_backends: 9
- product_modes: 5
- products: 5
- render_backends: 11
- storage_backends: 6
- toolchains: 7

Missing sections:
- none

Missing statuses:
- none

Invalid statuses:
- none

Invalid tiers:
- none

Missing evidence:
- none

Warnings:
- none

Strict-mode result: pass
```

### docs sanity - PASS

```text
Docs sanity OK.
```

### build target boundaries - PASS

```text
BOUNDARY-OK: build boundary checks passed
```

### UI shell purity - PASS

```text
UI shell purity OK.
```

### ABI boundaries - PASS

```text
ABI boundary check OK.
```

### focused RepoX - FAIL

```text
Test project C:/Inbox/Git Repos/dominium/out/build/vs2026/verify
    Start 291: inv_repox_rules
1/1 Test #291: inv_repox_rules ..................***Failed  146.59 sec
INV-DOC-STATUS-HEADER: invalid status 'DRAFT' in docs/repo/root-recycling/MOVE_BULK_00_GLOBAL_BAD_ROOT_MIGRATION_PLAN.md
INV-DOC-STATUS-HEADER: invalid status 'DRAFT' in docs/repo/root-recycling/MOVE_BULK_01_DOCS_ARCHIVE_APPLY_RESULT.md
INV-DOC-STATUS-HEADER: invalid status 'DRAFT' in docs/repo/root-recycling/MOVE_BULK_BATCH_SEQUENCE.md
INV-DOC-STATUS-HEADER: missing status header: docs/repo/audits/MOVE_BULK_08_FINAL_ROOT_CLOSURE_AUDIT.md
INV-DOC-STATUS-HEADER: missing status header: docs/repo/root-recycling/MOVE_BULK_08_FINAL_EXCEPTION_CLOSURE.md


0% tests passed, 1 tests failed out of 1

Label Time Summary:
portability    = 146.59 sec*proc (1 test)
testx          = 146.59 sec*proc (1 test)

Total Test time (real) = 147.17 sec

The following tests FAILED:
	291 - inv_repox_rules (Failed)                          portability testx
Errors while running CTest
```

### git status - PASS

```text
## main...origin/main
 M .aide/context/latest-review-packet.md
 M .aide/context/latest-task-packet.md
 M .aide/ledgers/migration_ledger.jsonl
 M .aide/reports/latest-dominium-status.md
 M .aide/reports/latest-warning-disposition.md
 M docs/repo/MOVE_FAMILY_REGRESSION_REQUIREMENTS.md
 M docs/repo/POST_CONVERGE_NEXT_STEPS.md
 M docs/repo/root-recycling/MOVE_BULK_00_GLOBAL_BAD_ROOT_MIGRATION_PLAN.md
 M docs/repo/root-recycling/MOVE_BULK_BATCH_SEQUENCE.md
 M docs/repo/root-recycling/ROOT_RECYCLING_RUNBOOK.md
 M tools/migration/root_inventory.json
 M tools/migration/root_move_map.json
?? .aide/reports/MOVE-BULK-08-CLOSURE-blockers.md
?? .aide/reports/MOVE-BULK-08-CLOSURE-exception-actions.json
?? .aide/reports/MOVE-BULK-08-CLOSURE-next-readiness.json
?? .aide/reports/MOVE-BULK-08-CLOSURE-next-readiness.md
?? .aide/reports/MOVE-BULK-08-CLOSURE-reference-debt.md
?? .aide/reports/MOVE-BULK-08-CLOSURE-remaining-debt.json
?? .aide/reports/MOVE-BULK-08-CLOSURE-root-matrix.json
?? .aide/reports/MOVE-BULK-08-CLOSURE-root-matrix.md
?? .aide/reports/MOVE-BULK-08-CLOSURE-shim-debt.md
?? .aide/reports/MOVE-BULK-08-CLOSURE-status.md
?? .aide/reports/MOVE-BULK-08-CLOSURE-validation.md
?? docs/repo/audits/MOVE_BULK_08_FINAL_ROOT_CLOSURE_AUDIT.md
?? docs/repo/root-recycling/MOVE_BULK_08_FINAL_EXCEPTION_CLOSURE.md
```

### git diff check - PASS

```text
(no output)
```

### git diff cached check - PASS

```text
(no output)
```

### ignored local status - PASS

```text
!! .aide.local/
!! .dominium.local/
```

## Summary
Validation completed with 3 failure(s) or unavailable checks. Closure remains PARTIAL and not ready for post-restructure proof.

## Rerun After Metadata/Packet Repair

Generated: 2026-05-17T15:50:21Z

| Check | Result | Exit |
| --- | --- | ---: |
| AIDE doctor rerun | PASS | 0 |
| AIDE validate rerun | PASS | 0 |
| focused RepoX rerun | FAIL | 8 |
| git diff check rerun | PASS | 0 |

## Rerun Output Snippets

### AIDE doctor rerun - PASS

```text
AIDE Lite doctor
status: PASS
- repo_root: C:/Inbox/Git Repos/dominium
- PASS required: .aide/policies/token-budget.yaml
- PASS required: .aide/memory/project-state.md
- PASS required: .aide/memory/decisions.md
- PASS required: .aide/memory/open-risks.md
- PASS required: .aide/prompts/compact-task.md
- PASS required: .aide/prompts/evidence-review.md
- PASS required: .aide/prompts/codex-token-mode.md
- PASS required: .aide/context/ignore.yaml
- INFO Q09 status: missing
- INFO Q10 status: missing
- INFO Q11 status: missing
- INFO Q12 status: missing
- INFO Q13 status: missing
- INFO Q14 status: missing
- INFO Q15 status: missing
- INFO Q16 status: missing
- INFO Q17 status: missing
- INFO Q18 status: missing
- INFO Q19 status: missing
- INFO Q20 status: missing
- PASS snapshot exists: .aide/context/repo-snapshot.json
- PASS latest task packet exists: .aide/context/latest-task-packet.md
- PASS context artifact exists: .aide/context/repo-map.json
- PASS context artifact exists: .aide/context/repo-map.md
- PASS context artifact exists: .aide/context/test-map.json
- PASS context artifact exists: .aide/context/context-index.json
- PASS context artifact exists: .aide/context/latest-context-packet.md
- PASS verifier artifact exists: .aide/policies/verification.yaml
- PASS verifier artifact exists: .aide/verification/latest-verification-report.md
- PASS review artifact exists: .aide/verification/review-decision-policy.yaml
- PASS review artifact exists: .aide/context/latest-review-packet.md
- PASS token ledger artifact exists: .aide/policies/token-ledger.yaml
- PASS token ledger artifact exists: .aide/reports/token-baselines.yaml
- PASS token ledger artifact exists: .aide/reports/token-ledger.jsonl
- PASS token ledger artifact exists: .aide/reports/token-savings-summary.md
- PASS token ledger records: 16
- PASS golden task artifact exists: .aide/policies/evals.yaml
- PASS golden task artifact exists: .aide/evals/golden-tasks/README.md
- PASS golden task artifact exists: .aide/evals/golden-tasks/catalog.yaml
- PASS golden task definitions: 130
- PASS golden task report exists: .aide/evals/runs/latest-golden-tasks.json
- PASS golden task report exists: .aide/evals/runs/latest-golden-tasks.md
- PASS controller artifact exists: .aide/policies/controller.yaml
- PASS controller artifact exists: .aide/controller/README.md
- PASS controller artifact exists: .aide/controller/outcome-ledger.jsonl
- PASS controller artifact exists: .aide/controller/latest-outcome-report.md
- PASS controller artifact exists: .aide/controller/latest-recommendations.md
- PASS controller artifact exists: .aide/controller/failure-taxonomy.yaml
- PASS outcome ledger records: 7
- PASS routing artifact exists: .aide/policies/routing.yaml
- PASS routing artifact exists: .aide/models/README.md
- PASS routing artifact exists: .aide/models/providers.yaml
- PASS routing artifact exists: .aide/models/capabilities.yaml
- PASS routing artifact exists: .aide/models/routes.yaml
- PASS routing artifact
... truncated ...
```

### AIDE validate rerun - PASS

```text
AIDE Lite validate
status: PASS
- PASS required file: .aide/policies/token-budget.yaml
- PASS required file: .aide/memory/project-state.md
- PASS required file: .aide/memory/decisions.md
- PASS required file: .aide/memory/open-risks.md
- PASS required file: .aide/prompts/compact-task.md
- PASS required file: .aide/prompts/evidence-review.md
- PASS required file: .aide/prompts/codex-token-mode.md
- PASS required file: .aide/context/ignore.yaml
- PASS context compiler config exists: .aide/context/compiler.yaml
- PASS context compiler config exists: .aide/context/priority.yaml
- PASS context compiler config exists: .aide/context/excerpt-policy.yaml
- PASS verifier config exists: .aide/policies/verification.yaml
- PASS verifier config exists: .aide/verification/evidence-packet.template.md
- PASS verifier config exists: .aide/verification/review-packet.template.md
- PASS verifier config exists: .aide/verification/review-decision-policy.yaml
- PASS verifier config exists: .aide/verification/diff-scope-policy.yaml
- PASS verifier config exists: .aide/verification/file-reference-policy.yaml
- PASS verifier config exists: .aide/verification/secret-scan-policy.yaml
- PASS XStack contract schema version is v0
- PASS XStack wrapper registry schema version is v0
- PASS XStack contract enforces no_apply true
- PASS XStack contract enforces execution_allowed false
- PASS XStack contract enforces apply_allowed false
- PASS XStack registry enforces no_apply true
- PASS XStack registry enforces execution_allowed false
- PASS XStack registry enforces apply_allowed false
- PASS XStack registry models XStack/AuditX/RepoX/TestX families
- PASS XStack registry contains wrapper plans for modeled systems
- PASS XStack registry detected xstack
- PASS XStack registry detected auditx
- PASS XStack registry detected repox
- PASS XStack registry detected testx
- PASS dominium.xstack.status execution_allowed false
- PASS dominium.xstack.status apply_allowed false
- PASS dominium.xstack.status no_apply true
- PASS dominium.auditx.status execution_allowed false
- PASS dominium.auditx.status apply_allowed false
- PASS dominium.auditx.status no_apply true
- PASS dominium.repox.policy execution_allowed false
- PASS dominium.repox.policy apply_allowed false
- PASS dominium.repox.policy no_apply true
- PASS dominium.testx.status execution_allowed false
- PASS dominium.testx.status apply_allowed false
- PASS dominium.testx.status no_apply true
- PASS dominium.buildx.status execution_allowed false
- PASS dominium.buildx.status apply_allowed false
- PASS dominium.buildx.status no_apply true
- PASS dominium.validation.profiles execution_allowed false
- PASS dominium.validation.profiles apply_allowed false
- PASS dominium.validation.profiles no_apply true
- PASS XStack integration excludes forbidden phrase: "execution_allowed": true
- PASS XStack integration excludes forbidden phrase: "apply_allowed": true
- PASS XStack integration excludes forbidden phrase: safe_to_delete
- PASS XStack i
... truncated ...
```

### focused RepoX rerun - FAIL

```text
Test project C:/Inbox/Git Repos/dominium/out/build/vs2026/verify
    Start 291: inv_repox_rules
1/1 Test #291: inv_repox_rules ..................***Failed  128.64 sec
INV-DOC-STATUS-HEADER: missing status header: docs/repo/audits/MOVE_BULK_08_FINAL_ROOT_CLOSURE_AUDIT.md
INV-DOC-STATUS-HEADER: missing status header: docs/repo/root-recycling/MOVE_BULK_08_FINAL_EXCEPTION_CLOSURE.md


0% tests passed, 1 tests failed out of 1

Label Time Summary:
portability    = 128.64 sec*proc (1 test)
testx          = 128.64 sec*proc (1 test)

Total Test time (real) = 128.79 sec

The following tests FAILED:
	291 - inv_repox_rules (Failed)                          portability testx
Errors while running CTest
```

### git diff check rerun - PASS

```text
(no output)
```

## Final Validation Disposition

First rerun still had a focused RepoX status-header failure; this was addressed by a second focused RepoX rerun below.
## Focused RepoX Second Rerun

Generated: 2026-05-17T15:53:35Z

| Check | Result | Exit |
| --- | --- | ---: |
| focused RepoX second rerun | PASS | 0 |

### focused RepoX second rerun - PASS

```text
Test project C:/Inbox/Git Repos/dominium/out/build/vs2026/verify
    Start 291: inv_repox_rules
1/1 Test #291: inv_repox_rules ..................   Passed  118.63 sec

100% tests passed, 0 tests failed out of 1

Label Time Summary:
portability    = 118.63 sec*proc (1 test)
testx          = 118.63 sec*proc (1 test)

Total Test time (real) = 118.72 sec
```

## Updated Final Validation Disposition

Focused RepoX passed after adding required status metadata to the new closure docs. Closure remains PARTIAL because root/batch blockers remain.
