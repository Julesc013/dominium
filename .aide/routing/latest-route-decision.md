# AIDE Latest Route Decision

## ROUTE_DECISION

- route_id: q17.latest
- task_source: `.aide/context/latest-task-packet.md`
- task_class: bounded_code_patch
- risk_class: medium
- route_class: local_strong
- fallback_route_class: cheap_remote
- hard_floor_applied: none
- blocked: false
- blocked_reason: none

## QUALITY_GATES

- token_budget_status: within_budget
- verifier_status: WARN
- golden_task_status: PASS
- outcome_recommendation_status: WARN
- quality_gate_status: WARN

## RATIONALE

- Classified task as bounded_code_patch with medium risk from compact task goal/phase text.

## REQUIRED_CHECKS

- evidence_packet_required_for_review
- golden_tasks_required_for_token_optimization
- token_budget_required_for_prompt_surfaces
- verifier_required_for_checkable_work

## EVIDENCE_SOURCES

- `.aide/context/latest-context-packet.md`
- `.aide/context/latest-task-packet.md`
- `.aide/evals/runs/latest-golden-tasks.json`
- `.aide/models/hard-floors.yaml`
- `.aide/models/routes.yaml`
- `.aide/policies/provider-adapters.yaml`
- `.aide/policies/routing.yaml`
- `.aide/providers/provider-catalog.yaml`
- `.aide/reports/token-savings-summary.md`
- `.aide/verification/latest-verification-report.md`

## SAFETY

- advisory_only: true
- provider_or_model_calls: none
- network_calls: none
- automatic_execution: false
- automatic_policy_mutation: false
- gateway_behavior: false
- contents_inline: false

## NOTES

- advisory_only: true
- provider_or_model_calls: none
- network_calls: none
- route_decisions_apply_automatically: false
- provider_candidates_metadata_only: local_ollama, local_lm_studio, local_llama_cpp, local_vllm, local_sglang
- provider_adapter_live_calls_allowed: false
