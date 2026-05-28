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

# Cross-Corpus Reconciliation

Cross-corpus reconciliation compares current docs, archive docs, conversation-derived outputs, and current repo authority.

## Finding Counts

- Drift/contradiction review findings: 136
- Duplicate shadows: 21

## Required Topics Covered

| Topic | Classification |
| --- | --- |
| Project identity and purpose | current_repo_truth |
| Canon and glossary authority | current_repo_truth |
| Engine/game/runtime/product boundaries | consistent_but_review_required |
| Determinism, replay, and provenance | current_repo_truth |
| Process-only mutation | current_repo_truth |
| Law, authority, refusal, and capability model | current_repo_truth_with_review_needed |
| Pack-driven integration | current_repo_truth |
| Profiles over runtime mode flags | current_repo_truth |
| Workbench/AIDE/Codex/tooling role | blocked_scope_sensitive |
| Conversation corpus role | conversation_advisory_only |
| Release/setup/launcher/platform state | blocked_scope_sensitive |
| Renderer/UI/native GUI scope | blocked_by_current_queue |
| Provider/package runtime scope | blocked_by_current_queue |
| Gameplay/domain feature scope | blocked_by_current_queue |
| Timekeeping and 2038 resilience | conversation_advisory_or_docs_candidate |
| World, reality, civilization, and worldgen domains | authority_sensitive |
| Contracts, schema, and reference docs | contract_or_schema_authority |
| Testing, validation, FAST, and full-gate debt | current_repo_truth_with_debt_tracking |
| Current queue blocked areas | current_repo_truth |


## Where To Inspect Detail

- `_reconciliation/DOCS_REPO_TRUTH_CROSSWALK_v0.md`
- `_audit/DOCS_DRIFT_MATRIX_v0.md`
- `_audit/DOCS_CONTRADICTION_MATRIX_v0.md`
- `_audit/DOCS_STALENESS_AND_VERIFICATION_v0.md`
