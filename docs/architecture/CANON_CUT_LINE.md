# Canon Cut-Line (CONS-0)

Status: binding.
Scope: canonical cut-line and precedence.

## Canonical cut-line
The canonical cut-line is the first explicit mention of "SLICE-1" in repository
history (prompts or documents). All prompts, decisions, and documents committed
before that mention are committed canon.

If "SLICE-1" has not yet appeared, all current material is canon and the first
future explicit mention of "SLICE-1" establishes the cut-line.

## Committed canon (binding)
The following are binding and MUST NOT be reinterpreted:
- `docs/architecture/*`
- All prompts, decisions, and documents before the cut-line
- Engine and game invariants
- UPS (Universal Pack System)
- TESTX invariants and enforcement model
- Determinism, authority, epistemics, and process-driven simulation
- Agents and institutions
- Worldgen contracts
- UI parity rules (CLI/TUI/GUI)
- Zero-asset guarantees

## Planning only (non-binding)
Anything discussed after the cut-line is planning only, including:
- Slice ladder (0-3)
- Playable slice definitions
- Earth/life/hominid coverage roadmap
- MVP shell expectations

## Precedence
Canon > prompts > plans > ideas.

No future prompt, plan, or idea may reinterpret canon. If a conflict exists,
canon wins and the conflicting material is invalid until corrected.
