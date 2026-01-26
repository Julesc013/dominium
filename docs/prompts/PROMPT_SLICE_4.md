PROMPT SLICE-4 - LIVE EVOLUTION, PLAYTESTING, AND SYSTEM CONVERGENCE
TARGET: GPT-5.2 CODEX
SCOPE: engine/ + game/ + data/ + client/ + tools/ + docs/arch/ + docs/dev/ + tests/
INTENT: ENABLE CONTINUOUS PLAYTESTING, RAPID OR SLOW ITERATION, AND SAFE OVERHAUL OF SYSTEMS UNTIL THE GAME CONVERGES

SYSTEM ROLE
You are operating inside the Dominium / Domino repository.
You are acting as:
- long-horizon systems integrator
- playtest infrastructure architect
- controlled-refactor gatekeeper

This prompt does NOT add a new slice of "gameplay".
It adds the machinery that allows the game to become complete without collapsing its architecture.

============================================================
ABSOLUTE CANON (BINDING)
============================================================

You MUST treat as law:

- docs/arch/*
- PROMPT CONS-0
- PROMPT WD-0
- PROMPT SLICE-0
- PROMPT SLICE-1
- PROMPT SLICE-2
- PROMPT SLICE-3
- UPS, TESTX, authority/law, epistemics, process model
- CLI/TUI/GUI parity
- Zero-asset executable requirement
- Extend-vs-create rule

SLICE-4 MUST NOT invalidate any prior slice contracts.

============================================================
PURPOSE OF SLICE-4
============================================================

SLICE-4 answers one question:

> "Can Dominium be played, tested, measured, and changed continuously
> without breaking saves, mods, determinism, or mental models -
> until it converges into a finished game?"

If yes, SLICE-4 is complete.

============================================================
ANTI-HARDCODING RULE (CRITICAL)
============================================================

You MUST NOT:
- hardcode final mechanics
- freeze balance assumptions
- embed "intended gameplay"
- add era logic
- add irreversible shortcuts

You MUST:
- design all new behavior as replaceable layers
- expect every system to be revised multiple times
- support coexistence of old and new implementations

============================================================
PART I - PLAYTEST HARNESS (FOUNDATIONAL)
============================================================

------------------------------------------------------------
A) PLAYTEST MODES
------------------------------------------------------------

You MUST define explicit playtest modes (policies, not systems):

Examples:
- sandbox_playtest
- hardcore_sim
- accelerated_time
- chaos_testing
- regression_playback

Playtest modes MUST be:
- implemented via policy/law/capability
- selectable at world creation or load
- auditable and replayable

------------------------------------------------------------
B) PLAYTEST CONTROL SURFACE
------------------------------------------------------------

Expose via CLI/TUI/GUI:

- pause / step / fast-forward
- seed override (explicit)
- controlled random perturbation (if enabled)
- scenario injection (non-authoritative)

All controls submit intent; nothing mutates directly.

============================================================
PART II - HOT-SWAPPABLE SYSTEM VARIANTS
============================================================

------------------------------------------------------------
A) VARIANT REGISTRY
------------------------------------------------------------

You MUST support system variants for iteration:

Examples:
- planning algorithm variants
- delegation heuristics
- failure propagation models
- ecology spread models
- trade valuation models

Variants MUST:
- share the same interfaces
- be capability-selected
- coexist in the same binary
- be selectable per-world or per-run

NO #ifdef gameplay logic.

------------------------------------------------------------
B) SAFE COEXISTENCE
------------------------------------------------------------

Old and new variants MUST:
- be loadable simultaneously
- operate on the same data
- produce comparable events
- be diffable via tooling

============================================================
PART III - INSTRUMENTATION & METRICS (NOT BALANCE)
============================================================

------------------------------------------------------------
A) METRICS AS OBSERVATIONS
------------------------------------------------------------

Metrics MUST be:
- read-only
- derived from snapshots/events
- never used to drive simulation directly

Examples:
- failure rates
- bottleneck frequency
- agent idle time
- institution stability

------------------------------------------------------------
B) METRIC SCOPING
------------------------------------------------------------

Metrics MUST be scoped by:
- slice
- domain
- time window
- policy mode

No global hidden counters.

============================================================
PART IV - SYSTEM OVERHAUL WITHOUT SAVE BREAKAGE
============================================================

------------------------------------------------------------
A) MULTI-VERSION SUPPORT
------------------------------------------------------------

You MUST support:

- loading worlds created under older variants
- running them in:
  - authoritative
  - degraded
  - frozen
  - transform-only modes

------------------------------------------------------------
B) TRANSFORM PIPELINES (OPTIONAL)
------------------------------------------------------------

If semantics truly change:
- define explicit transform processes
- never mutate in place
- always preserve originals

------------------------------------------------------------
C) DEPRECATION POLICY
------------------------------------------------------------

Document:
- how a system is deprecated
- how long it remains supported
- how refusal is surfaced

============================================================
PART V - CONTENT & MOD ITERATION SUPPORT
============================================================

------------------------------------------------------------
A) CONTENT SWAPPING
------------------------------------------------------------

You MUST ensure:

- content packs can be added/removed between runs
- missing content causes explicit degradation
- playtests can compare content variants side-by-side

------------------------------------------------------------
B) MOD SAFETY DURING ITERATION
------------------------------------------------------------

Mod authors MUST be able to:
- target specific capabilities
- survive engine changes
- receive explicit refusal reasons

============================================================
PART VI - PLAYTEST-DRIVEN UX ITERATION
============================================================

------------------------------------------------------------
A) UX EXPERIMENTATION
------------------------------------------------------------

Allow:
- alternative UI layouts
- alternate visual encodings
- different information density

WITHOUT:
- changing simulation semantics
- adding UI-only mechanics

------------------------------------------------------------
B) FEEDBACK LOOPS
------------------------------------------------------------

Support:
- annotation of events during playtest
- bookmarking moments in replays
- exporting traces for analysis

============================================================
PART VII - REGRESSION & ANTI-ENTROPY MECHANISMS
============================================================

------------------------------------------------------------
A) REGRESSION GUARANTEES
------------------------------------------------------------

Every iteration MUST preserve:

- determinism under same inputs
- slice contract compliance
- save loadability
- replay validity

------------------------------------------------------------
B) AUTOMATED DETECTION
------------------------------------------------------------

Add TESTX suites for:

- behavioral drift detection
- variant comparison
- performance regression thresholds
- refusal semantic stability

============================================================
PART VIII - DEVELOPER EXPERIENCE (DX)
============================================================

------------------------------------------------------------
A) RAPID CYCLES
------------------------------------------------------------

Support:
- fast headless runs
- scenario scripts
- reduced-world testbeds
- time acceleration

------------------------------------------------------------
B) SLOW, DEEP RUNS
------------------------------------------------------------

Also support:
- long-horizon simulations
- overnight runs
- history accumulation tests

============================================================
PART IX - DOCUMENTATION OUTPUTS
============================================================

You MUST create/update:

docs/arch/
- SLICE_4_CONTRACT.md
- ITERATION_PHILOSOPHY.md

docs/dev/
- PLAYTESTING_GUIDE.md
- VARIANT_SYSTEM.md
- METRICS_AND_ANALYSIS.md
- SAFE_OVERHAUL.md

docs/roadmap/
- POST_SLICE_4_EVOLUTION.md

============================================================
PART X - TESTX REQUIREMENTS
============================================================

You MUST add tests proving:

- Variant swapping does not break determinism guarantees
- Old saves load under new variants safely
- Metrics do not affect simulation outcomes
- Playtest modes are auditable
- Regression is detected automatically
- No slice contract is violated by iteration

============================================================
ACCEPTANCE CRITERIA
============================================================

PROMPT SLICE-4 is complete when:

- The game can be played end-to-end
- Developers can iterate safely and repeatedly
- Systems can be replaced without refactor
- Playtests produce actionable insight
- Regression is mechanically prevented
- The architecture remains intact under change

END PROMPT SLICE-4
