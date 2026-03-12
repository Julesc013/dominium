Change: META-COMPUTE-0 deterministic compute budgeting, throttling, and coupling hooks
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

Touched Paths:
- src/meta/compute/compute_budget_engine.py
- src/meta/compile/compile_engine.py
- src/system/macro/macro_capsule_engine.py
- src/process/software/pipeline_engine.py
- tools/xstack/repox/check.py
- tools/xstack/auditx/check.py
- tools/auditx/analyzers/e305_unmetered_loop_smell.py
- tools/auditx/analyzers/e306_silent_throttle_smell.py
- tests/invariant/compute_budgeting_tests.py

Demand IDs:
- cyber.firmware_supply_attestation
- cyber.scada_red_team_drill
- fact.deadlock_free_signaling
- fact.power_sag_shedding

Notes:
- Compute metering is explicit and deterministic across SYS/COMPILE/PROC execution paths.
- Over-budget behavior is logged with explain contracts and deterministic throttling outcomes.
