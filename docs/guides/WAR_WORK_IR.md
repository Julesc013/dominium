Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# War Work IR Guide (ADOPT5)





Scope: authoritative war Work IR emission for engagements and occupation.





## Invariants


- War actions are event-driven and emitted as Work IR only.


- Deterministic ordering is mandatory.


- Law gates every authoritative action.





## Dependencies


- `docs/guides/WORK_IR_EMISSION_GUIDE.md`


- `docs/architecture/REALITY_LAYER.md`


- `docs/architecture/DEATH_AND_CONTINUITY.md`





This guide defines the authoritative WarSystem Work IR contract for engagements,


occupation, resistance, and interdiction. War is event-driven, budgeted, and


law-gated; no per-ACT combat loops are allowed.





## Scope





- Authoritative system (STRICT determinism class).


- IR-only migration state.


- Event-driven engagements, occupation/resistance, and interdiction.





## Task Structure





WarSystem emits tasks in a fixed, deterministic order:





Engagement pipeline:


1) `DOM_WAR_TASK_ENGAGEMENT_ADMIT`


2) `DOM_WAR_TASK_ENGAGEMENT_RESOLVE`


3) `DOM_WAR_TASK_APPLY_CASUALTIES`


4) `DOM_WAR_TASK_APPLY_EQUIPMENT_LOSSES`


5) `DOM_WAR_TASK_UPDATE_MORALE_READINESS`





Occupation / resistance:


6) `DOM_WAR_TASK_OCCUPATION_MAINTAIN`


7) `DOM_WAR_TASK_RESISTANCE_UPDATE`


8) `DOM_WAR_TASK_DISRUPTION_APPLY`





Interdiction / blockade:


9) `DOM_WAR_TASK_ROUTE_CONTROL_UPDATE`


10) `DOM_WAR_TASK_BLOCKADE_APPLY`


11) `DOM_WAR_TASK_INTERDICTION_SCHEDULE`


12) `DOM_WAR_TASK_INTERDICTION_RESOLVE`





Each task declares:


- AccessSets with explicit reads/writes.


- CostModels with bounded CPU/memory/bandwidth.


- Stable task IDs and commit ordering keys.





## Scheduling Rules





- `next_due_act` (legacy field name: `next_due_tick`, deprecated terminology) is driven by due queues; no background scans.


- Task emission order is deterministic and stable across runs.


- Phase ordering preserves engagement -> effects -> occupation -> interdiction.





## Amortization & Degradation





- Work uses `start_index` + `count` slices.


- Budgets cap per-ACT processing and preserve determinism.


- Degradation reduces fidelity tier or cadence; it never skips irreversible effects.





## Law & Capability Integration





- Law can refuse war actions entirely or per-scope.


- Refused operations emit no tasks and must be auditable.


- No silent fallback paths are allowed.





## Forbidden assumptions





- Per-ACT global combat scans.


- Direct combat resolution outside Work IR.


- Hidden bypass of law or capability checks.


- Nondeterministic reductions or ordering.





## See also


- `docs/architecture/INVARIANTS.md`
