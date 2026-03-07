Change: GR3 FAST integrity stabilization and enforcement hygiene

Touched Paths:
- data/meta/real_world_affordance_matrix.json
- docs/audit/WORKTREE_LEFTOVERS.md
- schema/meta/coupling_evaluation_record.schema
- src/process/software/pipeline_engine.py
- src/system/macro/macro_capsule_engine.py
- src/system/reliability/reliability_engine.py
- tools/xstack/sessionx/process_runtime.py

Demand IDs:
- surv.knap_stone_tools
- surv.hand_pump_irrigation
- engr.tolerance_stackup_debug
- engr.metrology_lab_flow

Notes:
- Links enforcement-only and analyzer-hygiene refactors to explicit player demand IDs.
- No gameplay semantics changed; updates are deterministic governance hardening.
