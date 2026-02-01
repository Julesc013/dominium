Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Work IR Emission Guide (EXEC4)





Scope: game-side emission contract for Work IR and Access IR.





## Invariants


- Authoritative work is emitted as Work IR + Access IR.


- Task IDs and AccessSet IDs are deterministic.


- Law targets are required for authoritative tasks.





## Dependencies


- `schema/execution/README.md`


- `docs/architecture/EXECUTION_MODEL.md`


- `docs/architecture/LAW_ENFORCEMENT_POINTS.md`





## Forbidden assumptions


- Game code may execute tasks directly.


- Undeclared reads/writes are acceptable.





## See also


- `docs/guides/INTEREST_SYSTEM_WORK_IR.md`


- `docs/guides/ECONOMY_WORK_IR.md`





This guide defines the **game-side contract** for emitting Work IR and Access IR.


Systems must **emit tasks**; they must never execute work directly.





## Start Here


- Implement `ISimSystem` in `game/core/execution/system_iface.h`.


- Register systems with `dom_system_registry`.


- Emit `dom_task_node`, `dom_access_set`, and `dom_cost_model` via the builders.





## Required Flow


1) **Register the system** with a stable `system_id`.


2) **Emit tasks** in `emit_tasks()` using deterministic inputs only.


3) **Declare AccessSets** (reads/writes/reduces) for every task.


4) **Attach CostModels** with upper bounds only.


5) **Let the engine scheduler execute**; game code never runs tasks directly.





## Stable Task IDs


Use the builder helper to derive stable IDs:


- Task ID: `dom_work_graph_builder_make_id(system_id, local_id, DOM_WORK_ID_TASK)`


- AccessSet ID: `dom_work_graph_builder_make_id(system_id, local_id, DOM_WORK_ID_ACCESS)`


- CostModel ID: `dom_work_graph_builder_make_id(system_id, local_id, DOM_WORK_ID_COST)`





Guidelines:


- `system_id` is a stable, deterministic identifier for the system.


- `local_id` is a stable, deterministic index within the system for the current emission.


- Never use pointer values, container iteration order, or timestamps for IDs.





## AccessSet Declaration


Every task must declare **all** access:


- Reads: `dom_access_set_builder_add_read(...)`


- Writes: `dom_access_set_builder_add_write(...)`


- Reduces: `dom_access_set_builder_add_reduce(...)` with deterministic `reduction_op`.





No hidden access and no implicit pointer-chasing are allowed.





## CostModel Declaration


Cost models are **upper bounds only**:


- `cpu_upper_bound`, `memory_upper_bound`, `bandwidth_upper_bound`


- `latency_class` and `degradation_priority`





Costs are estimates to support budgeting and degradation, not profiling data.





## Law Targets


Authoritative tasks **must** declare non-empty `law_targets`.


Targets are defined in `schema/law/SPEC_LAW_TARGETS.md`.





Numeric IDs should be derived deterministically from the token (e.g., FNV-1a 32 of


the ASCII token string) and documented in the emitting system.





## Common Anti-Patterns (Forbidden)


- Executing work directly inside `emit_tasks()`.


- Calling scheduler backends from game code.


- Emitting tasks without AccessSets or CostModels.


- Using nondeterministic IDs (addresses, wall-clock time).


- Hidden reads/writes that are not declared.


- Global scans or implicit background stepping.





## Minimal Example (Pseudo-Code)


```cpp


class ExampleSystem : public ISimSystem {


  int emit_tasks(dom_act_time_t now, dom_act_time_t target,


                 dom_work_graph_builder* graph,


                 dom_access_set_builder* access) {


    u64 task_id = dom_work_graph_builder_make_id(system_id(), 1u, DOM_WORK_ID_TASK);


    u64 access_id = dom_work_graph_builder_make_id(system_id(), 1u, DOM_WORK_ID_ACCESS);


    u64 cost_id = dom_work_graph_builder_make_id(system_id(), 1u, DOM_WORK_ID_COST);


    dom_task_node node = { /* fill fields deterministically */ };


    dom_cost_model cost = { /* upper bounds */ };


    dom_access_set_builder_begin(access, access_id, DOM_REDUCE_NONE, 0);


    dom_access_set_builder_add_read(access, &range);


    dom_access_set_builder_add_write(access, &range);


    dom_access_set_builder_finalize(access);


    dom_work_graph_builder_add_cost_model(graph, &cost);


    dom_work_graph_builder_add_task(graph, &node);


    return 0;


  }


};


```
