Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Process-Only State Mutation (PROC0)





Status: binding.


Scope: the only lawful path for authoritative state change.





## Constitutional rule


All authoritative state changes occur only via Process execution.





This rule applies to engine, game, server, tools, migrations, and recovery.





## What counts as a Process


A Process is any deterministic, law-admitted pipeline that:


- declares inputs and outputs by stable identifiers


- executes via Work IR and Access IR


- commits authoritative effects at deterministic commit points





A Process may be small or large. Size does not change the rule.





## "Simple" changes are still Processes


The following are still Processes even when they look trivial:


- movement between locations


- decay, growth, or maintenance updates


- transfers, exchanges, or inventory changes


- state toggles, flags, or mode changes


- repairs, crafting, or conversions





If it changes authoritative state, it is a Process.





## Forbidden mutation patterns


The following patterns violate PROC0:


- direct component writes outside a Process commit


- background scans that mutate state without explicit scheduling


- derived or presentation code writing authoritative state


- tool-side mutation that bypasses ToolIntents and law gates


- migration scripts that "fix up" live state without Process framing





## Required mutation pipeline (summary)


1. Intent admission via law gates.


2. Process selection and Work IR emission.


3. Task admission, execution, and deterministic ordering.


4. Commit gate and auditable authoritative effects.





## See also


- `docs/architecture/EXECUTION_MODEL.md`


- `docs/architecture/LAW_ENFORCEMENT_POINTS.md`


- `schema/process.schema`
