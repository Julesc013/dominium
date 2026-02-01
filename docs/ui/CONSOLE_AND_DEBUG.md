Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Console and Debug

Console:
- The CLI command set is canonical.
- GUI and TUI consoles are REPL shells over the same command parser.
- Commands submit intent; they do not mutate state directly.
- Refusals use stable codes and structured details.

Minimum command surface (SLICE-0):
- `templates`
- `new-world` (plus parameters)
- `load-world` (path or default)
- `save` (path or default)
- `inspect-replay` (path or default)
- `mode <policy.mode.*>`
- `where`
- `exit`

Debug overlay:
- Read-only by default.
- Must display:
  - snapshot stats (counts, tick/time)
  - event stream tail
  - authority tokens held
  - active capabilities/policies
- Any mutating debug action must go through law/policy and emit events.

HUD (minimal):
- world identifier
- current topology node
- coordinate frame and position
- active policy layers
- simulation time/tick