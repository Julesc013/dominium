Status: CANONICAL
Last Reviewed: 2026-04-07
Supersedes: none
Superseded By: none
Stability: stable
Future Series: post-baseline AIDE roadmapping and extraction-admission review
Replacement Target: later explicit post-baseline AIDE roadmap checkpoint or approved replacement closure checkpoint only
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `docs/planning/CHECKPOINT_C_ZETA_MEGA_VALIDATION_AND_CLOSURE.md`, `data/planning/checkpoints/checkpoint_c_zeta_mega_validation_and_closure.json`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZETA.md`, `data/planning/next_execution_order_post_zeta.json`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_SYSTEM_INVENTORY.md`, `docs/audit/ULTRA_REPO_AUDIT_ENTRYPOINTS_AND_RUNPATHS.md`, `docs/audit/ULTRA_REPO_AUDIT_PRODUCT_ASSEMBLY_PLAN.md`, `docs/audit/ULTRA_REPO_AUDIT_PLAYTEST_READINESS.md`, `docs/audit/ULTRA_REPO_AUDIT_REUSE_AND_CONSOLIDATION_PLAN.md`, `docs/audit/ULTRA_REPO_AUDIT_BUILD_RUN_TEST_MATRIX.md`, `docs/audit/ULTRA_REPO_AUDIT_WIRING_MAP.md`, `docs/audit/ULTRA_REPO_AUDIT_GAPS_AND_TODOS.md`, `data/audit/ultra_repo_audit_entrypoints.json`, `data/audit/ultra_repo_audit_product_assembly_plan.json`, `data/audit/ultra_repo_audit_gap_ledger.json`, `data/audit/ultra_repo_audit_build_run_test_matrix.json`, `data/audit/ultra_repo_audit_wiring_map.json`, `docs/xstack/XSTACK_SCOPE_FREEZE.md`, `data/xstack/xstack_scope_freeze.json`, `docs/xstack/XSTACK_INVENTORY_AND_CLASSIFICATION.md`, `data/xstack/xstack_inventory_and_classification.json`, `docs/xstack/AIDE_PORTABLE_TASK_CONTRACT.md`, `data/xstack/aide_portable_task_contract.json`, `docs/xstack/AIDE_EVIDENCE_AND_REVIEW_CONTRACT.md`, `data/xstack/aide_evidence_and_review_contract.json`, `docs/xstack/AIDE_POLICY_AND_PERMISSION_SHAPE.md`, `data/xstack/aide_policy_and_permission_shape.json`, `docs/xstack/AIDE_CAPABILITY_PROFILE_SHAPE.md`, `data/xstack/aide_capability_profile_shape.json`, `docs/xstack/AIDE_ADAPTER_CONTRACT.md`, `data/xstack/aide_adapter_contract.json`, `docs/xstack/CODEX_REPO_OPERATING_CONTRACT.md`, `data/xstack/codex_repo_operating_contract.json`, `docs/xstack/XSTACK_TO_AIDE_EXTRACTION_MAP.md`, `data/xstack/xstack_to_aide_extraction_map.json`, `tools/xstack/session_create.py`, `tools/xstack/session_boot.py`, `tools/xstack/testx_all.py`, `tools/validation/tool_run_validation.py`, `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `release/release_manifest_engine.py`, `security/trust/trust_verifier.py`

# C-XSTACK-AIDE Closure

## A. Purpose And Scope

This checkpoint closes the XStack/AIDE narrowing-and-contract phase.

It evaluates whether `X-0` through `X-8` completed the intended mission:

- freeze what XStack means now in the live repo
- inventory and classify XStack/AIDE-relevant surfaces
- freeze the portable task contract
- freeze the portable evidence/review contract
- freeze the portable policy/permission shape
- freeze the portable capability-profile shape
- freeze the portable adapter contract
- freeze the Codex repo operating contract
- freeze the XStack-to-AIDE extraction boundary map

This checkpoint does not:

- implement an AIDE runtime
- perform code extraction or repo migration
- reopen the scope freeze without cause
- compete with the canonical playable-baseline assembly path
- treat contract or planning freezes as completed runtime/platform work

## B. Current Phase State

This is the closure checkpoint for the XStack/AIDE narrowing-and-contract phase.

The phase is subordinate to the current repo priority:

- the admissible `Zeta` doctrine and gating program is complete
- the immediate engineering priority remains the canonical repo-local playable baseline
- the ultra audit still points to startup/session/bootstrap hardening, not broad platformization, as the highest-value next move

The XStack/AIDE phase therefore closes as a narrowing, contract-freeze, and extraction-boundary phase only.

## C. Family-By-Family Completion Review

| Family | Verdict | Why |
| --- | --- | --- |
| XStack scope freeze | `complete` | `X-0` produced a canonical definition of XStack, scope buckets, in-scope versus out-of-scope rules, and Dominium-retained boundaries. |
| Inventory and classification | `complete_with_cautions` | `X-1` produced a detailed live-surface ledger and reuse/extraction classifications, but some surfaces remain explicitly mixed, legacy, or later-review only. |
| Portable task contract | `complete` | `X-2` froze the portable task-unit shape and kept runtime/scheduler semantics out of scope. |
| Evidence/review contract | `complete` | `X-3` froze portable evidence and review semantics, including refusal, rejection, acknowledgement, approval, and escalation boundaries. |
| Policy/permission shape | `complete` | `X-4` froze portable policy and permission declarations while keeping enforcement/runtime machinery in Dominium or deferred. |
| Capability-profile shape | `complete` | `X-5` froze portable capability-profile declaration shape and its contract links without inventing a resolver/runtime. |
| Adapter contract | `complete` | `X-6` froze the portable adapter declaration and compatibility/failure semantics without creating adapter machinery. |
| Codex repo operating contract | `complete_with_cautions` | `X-7` froze one canonical build/validation/playtest/session rule set, but it honestly preserves the current baseline blockers and does not pretend the one-command playtest path is already fully solved. |
| XStack-to-AIDE extraction map | `complete_with_cautions` | `X-8` produced the extraction-boundary ledger and staged post-baseline extraction order, but it intentionally defers mixed and baseline-critical surfaces instead of forcing premature portability claims. |

## D. Portable Core Vs Dominium-Retained Summary

### Portable Now

Portable now means semantically frozen and reusable at the document-first or contract-first layer, not already extracted into a separate AIDE runtime.

Portable now includes:

- the frozen XStack meaning and scope buckets from `X-0`
- the portable contract family from `X-2` through `X-6`
- the document-first extraction-ready semantic core identified in `X-8`
- the strongest future code-light portable-core candidates already called out by `X-1` and `X-8`:
  - `tools/xstack/core/**`
  - low-level `tools/xstack/compatx/**` contract primitives such as canonical JSON, validator helpers, and schema-registry-oriented substrate

### Dominium-Retained Now

These remain Dominium-owned for now:

- session creation, boot, runtime control, and save-root-sensitive paths
- AppShell, launcher, setup, and operator-command surfaces
- local loopback authority, local singleplayer bridge, and baseline runtime glue
- pack, profile, lock, registry-compile, and packaging/distribution pipelines
- release/trust consumers and repo-specific verification/publication behavior
- validation/reporting surfaces whose current implementation still owns repo suites, report sinks, or Xi-specific policy
- the repo-operating contract itself, which is a Dominium repo law surface rather than an AIDE artifact

### Deferred Until Post-Baseline

Deferred until after the canonical playable baseline exists:

- full AIDE runtime, daemon, scheduler, compiler, bakeoff, or worker-pool work
- code extraction or repo migration
- a separate AIDE repo
- broad adapter implementation or adapter runtime selection machinery
- mixed-surface review for UI bind, validation kernels, CI guardrail policy, and gate/review bridge layers
- any attempt to extract baseline-critical session/runtime or AppShell/operator surfaces

## E. Immediate Operational Value

These artifacts improve the repo now in five concrete ways.

### Codex Performance On The Repo

- future Codex runs now have one explicit repo-operating contract instead of inferring build, validation, playtest, and directory rules from drifted docs
- the XStack/AIDE packet reduces re-investigation time for scope, ownership, and portability questions

### Task Scoping

- prompts can distinguish portable-contract work from Dominium runtime work cleanly
- the series makes it easier to reject overbroad asks that try to smuggle in runtime/platform work under "AIDE" naming

### Repo Safety

- the packet freezes which families are protected, mixed, retained, deferred, or out of scope
- baseline-critical surfaces are explicitly shielded from premature extraction churn

### Future Extraction Clarity

- the repo now has a real extraction map instead of vague portability aspirations
- later AIDE work can start from staged extraction decisions, prerequisites, and shim requirements rather than reopening the whole repo classification problem

### Playable-Baseline Non-Interference

- the series now acts as a constraint set during baseline assembly rather than a competing workstream
- it tells Codex what to reuse, what to leave alone, and what not to broaden until the baseline is real

## F. Deferred Work Ledger

The following remains explicitly deferred until after the canonical playable baseline exists:

- full AIDE runtime implementation
- daemon, scheduler, worker-pool, compiler, bakeoff, or adapter-runtime machinery
- broad code extraction or repo migration
- separate AIDE repository creation
- broad wrapper or bridge implementation across the repo
- post-baseline review of mixed surfaces such as UI bind, validation unification kernels, CI guardrail policy, and gate/review bridges
- any extraction or promotion of session/runtime/AppShell/launcher/setup/local-loopback/release-trust paths
- any reopening of XStack meaning, scope buckets, or portable contract shapes without an explicit follow-up checkpoint

## G. Next-Step Handoff

The recommended next XStack/AIDE step after the playable baseline exists is:

- `AIDE_POST_BASELINE_ROADMAP-0`

That post-baseline prompt should:

- re-check the actual playable baseline against the X-7 repo operating contract and X-8 extraction map
- confirm which extraction prerequisites are now truly satisfied
- admit or refuse a first post-baseline extraction-review tranche
- define a wrapper/bridge plan for any candidates that are still coupled to Dominium-owned shells or runtime flows
- keep runtime implementation, code movement, and platformization out of scope unless a later explicit admission review authorizes them

No further XStack/AIDE prompt is required before the baseline exists.

Before the baseline exists, the existing X-series artifacts should only be used as:

- scoping law
- boundary law
- repo-operating guidance
- non-interference constraints during baseline assembly

## H. Anti-Patterns And Forbidden Follow-Ups

Forbidden follow-ups include:

- using closure to justify immediate AIDE platformization
- reopening the XStack scope freeze because a surface "sounds generic"
- extracting baseline-critical Dominium surfaces before the local playable baseline exists
- treating contract freezes as proof that runtime implementation is complete
- using the extraction map to justify broad renames, code movement, or repo splits now
- creating new XStack/AIDE prompts before the baseline that compete with startup/session/playtest hardening
- treating the repo-operating contract as an AIDE operating policy instead of a Dominium repo rule set

## I. Final Verdict

Final answers:

- Is the XStack/AIDE narrowing-and-contract phase complete?
  - `yes`
- Complete in what sense?
  - the intended narrowing, contract-freeze, repo-operating, and extraction-boundary mission is complete
- Did this phase complete runtime extraction or platform implementation?
  - `no`
- Is any further XStack/AIDE prompt required before the playable baseline exists?
  - `no`
- What is the next XStack/AIDE prompt after the playable baseline exists?
  - `AIDE_POST_BASELINE_ROADMAP-0`

The phase is therefore closed as a successful document-first and boundary-first program that should now sit behind the playable-baseline path rather than in front of it.
