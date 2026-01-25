# AG-2 MVP Completion

Scope: engine/ + game/ + data/ + docs/agents for AG-2 (institutions, power, contracts, conflict, macro-history).

Validation artifacts:
- `engine/tests/agent_mvp_social_tests.cpp` (headless, no assets)

Coverage matrix:
- Institutions are agents: `test_institutions_are_agents`
- Authority grant/revoke: `test_authority_grant_revoke`
- Constraints block actions: `test_constraints_block_actions`
- Contracts bind and fail: `test_contracts_bind_and_fail`
- Conflict and institutional collapse: `test_conflict_and_collapse`
- History records conflict/collapse and determinism: `test_history_macro_determinism`

Notes:
- Tests use deterministic fixed-point/integer inputs only.
- History aggregation uses audit events for macro-history narratives.
