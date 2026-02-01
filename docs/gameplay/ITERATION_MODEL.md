Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Iteration Model

This model defines how playtests are assembled and compared without adding gameplay rules.

**Scenarios**
- Scenarios are data-only descriptions of the initial state.
- A scenario declares the world template, seed, policies, and optional initial adjustments.
- Scenarios do not embed code and do not alter simulation semantics.

**Variants**
- Variants are data-only overrides applied at load time.
- Variants can adjust policies, seed, and variant selections.
- Variants are recorded in replays to preserve deterministic provenance.

**Play Modes**
- Play modes are policy sets, not code paths.
- Examples: singleplayer, coop, server.authoritative, server.anarchy, spectator, inspect-only.
- Changing mode must not change simulation semantics, only policy constraints.

**Replay-First**
- Every session can emit a replay that includes scenario metadata, variants, and events.
- Replays are deterministic and reloadable in inspect-only mode.
- Replays are the primary artifacts for regression, comparison, and metrics.

**Metrics**
- Metrics are derived from event streams, not hidden counters.
- Refusal counts, process counts, and domain transitions are computed from events.

**Safety**
- Scenario reload is clean and resets prior state.
- Variant swaps are applied at load time and recorded explicitly.
- Failures and refusals are explicit, deterministic, and replayable.