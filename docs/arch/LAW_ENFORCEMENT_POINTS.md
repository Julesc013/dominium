# Law Enforcement Points (EXEC0c)

Status: binding.
Scope: mandatory law gates for commands, tasks, commits, and information.
Authority: ARCH0, then EXEC0, then EXEC0b.

## Purpose
Define the canonical enforcement points where the Law Kernel must be invoked so
no work executes or emits information without legal permission.

## Enforcement Phases (Mandatory)
1) Command Admission Gate (pre-scheduling)
   - Every CommandIntent is evaluated before it can become work.
2) Task Admission Gate (pre-execution)
   - Every TaskNode is evaluated before it can run.
3) Effect Commit Gate (pre-state-mutation)
   - Any authoritative writes are gated before commit.
4) Information Emission Gate (EIL and tools)
   - Any emission of information is law/capability gated.
5) Network Admission Gate
   - Client join, client integrity, and modified client policy.

All five gates MUST use the same Law Kernel.

## Task Admission Contract (Work IR)
TaskNode must declare:
- law_targets[] (non-empty for AUTHORITATIVE tasks)
- law_scope_ref
- actor_ref (optional)
- capability_set_ref (optional)
- policy_params (deterministic)

Execution backends MUST:
- call the law kernel before running any task,
- honor ACCEPT/REFUSE/TRANSFORM/CONSTRAIN outcomes,
- record an audit trail.

Law evaluation MUST NOT:
- inspect data not present in the declared context,
- depend on wall-clock time,
- depend on randomness.

## Effect Commit Gate
Authoritative writes are committed only after a law gate decision at commit
time. This avoids ambiguity where compute is allowed but commit is forbidden.

## Information Emission Gate
UI, tools, and advisory outputs are gated by law and capability. This gate
applies to derived tasks and to any emission of information across the
epistemic boundary.

## Cross-References
- Law kernel: `schema/law/SPEC_LAW_KERNEL.md`
- Scopes: `schema/law/SPEC_LAW_SCOPES.md`
- Targets: `schema/law/SPEC_LAW_TARGETS.md`
- Effects: `schema/law/SPEC_LAW_EFFECTS.md`
