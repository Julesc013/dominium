Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# AG-1 MVP Validation

Scope: engine/ + game/ + docs/agents/ for AG-1 (intent, planning, knowledge, memory, failure).

Validation artifacts:
- `engine/tests/agent_mvp_core_tests.cpp` (headless, no assets)

Coverage matrix:
- Multiple goals and arbitration: `test_multiple_goals`
- Subjective knowledge only: `test_subjective_knowledge_only`
- Divergent beliefs: `test_divergent_beliefs`
- Failure affects planning: `test_failure_affects_planning`
- Wrong belief repeats failure: `test_wrong_belief_repeats_failure`
- Failure updates beliefs: `test_failure_updates_belief`
- Memory decay changes behavior: `test_memory_decay_changes_behavior`
- History emission and determinism: `test_history_and_determinism`

Notes:
- Tests are deterministic and rely on fixed integer math only.
- History entries include timestamps and provenance via `dom_agent_audit_log`.