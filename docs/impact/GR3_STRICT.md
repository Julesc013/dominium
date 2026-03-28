Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Change: GR3 STRICT invariant unblock (action family coverage + field token hygiene)
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

Touched Paths:
- data/registries/action_template_registry.json
- meta/__init__.py
- tools/xstack/sessionx/process_runtime.py
- tools/xstack/testx/tests/test_hidden_state_violation_detected.py
- docs/audit/WORKTREE_LEFTOVERS.md

Demand IDs:
- surv.knap_stone_tools
- engr.metrology_lab_flow
- fact.automated_rework_loop

Notes:
- Adds missing `task.assay`, `task.disassemble`, and `task.scan` action-template family mappings required for deterministic process/task grammar coverage.
- Removes a false-positive `field.get` token in runtime hashing code without changing behavior.
- Breaks a strict import cycle by lazy-loading META-REF exports in `meta/__init__.py`.
- Aligns hidden-state guard test fixture with profile resolution path (no legacy debug toggle).
