Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-WORKFLOW-LAW-01
Stability: provisional
Binding Sources: `.aide/policies/recovery.yaml`, `.aide/policies/repair-classes.yaml`, `.aide/policies/work-units.yaml`

# AIDE Blocker Taxonomy

| Blocker | Description | Severity | Default Action | Class | Required Evidence | Branch Behavior |
| --- | --- | --- | --- | --- | --- | --- |
| `dirty_worktree_unrelated` | Dirty files are path-disjoint from current task. | warning | Continue without staging unrelated files. | continue | `git status`, path classification, allowed paths. | Stay on current task branch; preserve unrelated work. |
| `dirty_worktree_same_task` | Dirty files are part of the same task continuation. | info | Continue and include in evidence. | continue | Diff summary, task ID link. | Continue on same task branch. |
| `merge_conflict` | Merge or patch conflict blocks integration. | error | Resolve if owned; otherwise create repair task. | repair | Conflict paths, owner, resolution evidence. | Use task/repair/checkpoint lane as appropriate. |
| `validator_failure_repairable` | Validation failed for a fixable in-scope issue. | error | Repair in scope and rerun targeted validation. | repair | Command, exit code, output summary, fix refs. | Continue on task or repair branch. |
| `validator_failure_policy` | Validation failure shows policy or contract mismatch. | error | Stop or create policy/prereq task. | create_prerequisite | Failed rule, affected authority, required policy. | Do not integrate until policy disposition exists. |
| `missing_prerequisite` | Required upstream task, schema, or artifact is absent. | error | Create prerequisite task; do not fake completion. | create_prerequisite | Missing artifact/task ID, dependency reason. | Mark current task `BLOCKED_MISSING_PREREQ`. |
| `missing_tool` | Required local tool is absent or not runnable. | warning | Use existing alternative if equivalent; otherwise prerequisite task. | create_prerequisite | Tool name, attempted command, alternative check. | Continue only when equivalent validation exists. |
| `missing_connector` | Requested connector is unavailable. | warning | Record missing connector; use local fallback only if allowed. | ask_human | Connector name, request context, fallback scope. | No live connector assumptions. |
| `missing_capability` | Repo lacks declared capability required for scope. | error | Create capability/prerequisite task. | create_prerequisite | Capability ID or missing surface. | Do not implement broad capability unless scoped. |
| `missing_secret` | External secret is required and unavailable. | error | Stop without requesting or writing secret values. | stop | Secret class without value, command need. | No commits that expose or guess secrets. |
| `unsafe_operation` | Requested action risks safety, trust, or authority violation. | error | Stop and report exact risk. | stop | Risk statement, affected paths, policy ref. | Use quarantine if evidence must be preserved. |
| `destructive_git_required` | Progress appears to require reset, checkout overwrite, force-push, or delete. | error | Stop for human decision. | ask_human | Command required, affected refs/paths. | No destructive git action autonomously. |
| `architecture_decision_required` | Task requires semantic/architecture choice not already authorized. | error | Ask human or create decision task. | ask_human | Decision subject, candidates, authority refs. | Mark blocked; do not choose by convenience. |
| `human_review_required` | Review gate is explicit in doctrine or task packet. | error | Stop at review gate. | ask_human | Gate name, reviewed artifacts needed. | No promotion beyond gate. |
| `test_timeout` | Test timed out without clear deterministic failure. | warning | Retry once if bounded; otherwise classify as flaky or repair. | repair | Timeout command, duration, retry result. | Continue only with recorded timeout disposition. |
| `flaky_test_suspected` | Test instability is suspected. | warning | Rerun bounded sample and record flake suspicion. | repair | Pass/fail sequence and environment. | Do not call clean pass unless stable enough by policy. |
| `generated_artifact_drift` | Generated evidence is stale relative to sources. | warning | Refresh if in scope or create repair task. | repair | Source/artifact refs, generator command. | Do not promote stale generated evidence. |
| `stale_queue_state` | Queue/current or status contradicts live evidence. | error | Reconcile if assigned; otherwise stop for coordination. | repair | Stale fields, live refs, proposed update. | Only coordinator edits queue. |
| `stale_context_packet` | Latest context/task/review packet no longer reflects task state. | warning | Refresh if assigned; otherwise record stale packet. | repair | Packet path, mismatch, replacement source. | Only assigned packet owner edits latest packets. |
| `source_authority_conflict` | Same-tier or stronger sources conflict materially. | error | Stop and escalate; do not invent winner. | stop | Conflicting sources, authority domain, impact. | Quarantine until reviewed. |

## Severity Meaning

- `info`: record and continue.
- `warning`: continue only with bounded evidence or repair path.
- `error`: requires repair, prerequisite, human decision, or stop.
