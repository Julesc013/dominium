# Latest AIDE Intent Packet

- schema_version: aide.intent-packet.v0
- generated_by: aide-lite
- generated_from: inline_prompt
- raw_prompt_hash: 42a232463d80d4baed33a1535e7ddf281e7c028adcdc110c5d98c11157b710a5
- raw_prompt_excerpt: Plan the next bounded Dominium AIDE-controlled task from DCHECK-01 evidence
- interpreted_goal: Normalize prompt into a bounded evidence WorkUnit draft: draft the smallest safe WorkUnit after repo-state preflight.
- confidence: high
- task_class: evidence
- risk_class: external_side_effect
- sizing_class: audit_only
- safe_to_execute: false
- requires_split: false
- blocked: false
- blocker_reason: none
- next_action: draft the smallest safe WorkUnit after repo-state preflight
- task_execution: false
- provider_or_model_calls: none
- network_calls: none
- raw_long_prompt_storage: false

## Rejected Interpretations

- do not bypass queue, branch, evidence, or policy state
- do not execute raw prompt directly
- do not mutate target repositories from AIDE source repo

## Repo State Refs

- `.aide/context/latest-context-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/context/latest-task-packet.md`
- `.aide/queue/Q17/status.yaml`
- `.aide/queue/index.yaml`
- `.aide/repo/file-inventory.json`
- `.aide/repo/latest-repo-intelligence.md`
- `.aide/reports/file-quality-ledger.json`
- `.aide/reports/file-quality-summary.md`

## Branch State Refs

- current_branch:main
- current_role:canonical
- workflow:trunk_without_dev
- worktree_dirty:true

## Validation Hints

- `git diff --check`
- `py -3 .aide/scripts/aide_lite.py intent validate`

## Evidence Hints

- `changed-files.md`
- `validation.md`
- `remaining-risks.md`
- `intent-compiler-report.md`
