Status: DERIVED
Last Reviewed: 2026-06-03
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

# Contradictions And Drift

The archive preserves historical changes and conflicting levels of ambition. These should be classified rather than smoothed away.

- This chat is a major planning pivot. It began with a Windows UI Editor/Tool Editor design and ended with a broader Dominium Workbench Platform architecture. The old editor plan is superseded as a final product. Its useful pieces should be recycled into Workbench modules.
- - Did applied Codex prompts fully succeed? - Has launcher hardening already run? - Do command graph/UI IR/binding validator exist? - Does launcher run with zero packs and missing locale? - Does launcher refuse BUILD-ID mismatches? - Are any shared headers ambiguously owned?
- Earlier proposed layouts using `setup/adapters`, adapter-local packaging, and `core/source` were superseded. The canonical setup layout is `setup/core/{fetch,verify,install,rollback}`, `setup/include/{dsk,dsu}`, `setup/packages`, `setup/platform`, `setup/tests`, and `setup/ui`.
- - Domino = engine core; Dominium = game/runtime/tooling layer. - Specs are normative; README is descriptive. - 286+ full engine target; CP/M limited only. - Unified source hierarchy for all platforms. - No divergent port implementations. - Capability-based graceful degradation. - Lockstep is canonical. - Disk versions immutable. - `content.lock` mismatch fatal until reconciled.
- - Candidates: `135` - Source conversations represented: `45` - Noisy or archival-process candidates: `17` - Overlong candidates: `44` - Candidates with `not_checked` repo conflict: `135`
- At the beginning, the discussion was narrow: the user was choosing fixed-point coordinate precision for a world divided into powers-of-two spatial units. That quickly expanded into a much larger architecture question: how should an enormous procedural world be represented, simulated, saved, streamed, rendered, modified, and extended without becoming inconsistent, bloated, or impossible to maintain?

## Common Drift Pattern

The most common drift pattern is old or advisory material describing a future product surface as if it were implementation-ready. Current queue state blocks broad renderer, native GUI, Workbench UI, provider runtime, package runtime, gameplay, and release publication until future reviewed phases open them.
