# Aggregator Packet — Dominium Timekeeping and 2038 Resilience

## Packet Metadata

* Chat label: Dominium Timekeeping and 2038 Resilience
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only unless labelled PROJECT-CONTEXT
* Coverage: substantial visible transcript plus selected Dominium repo files; not exhaustive
* Confidence: 4/5
* Staleness risk: medium
* Merge priority: high for Dominium time architecture
* Main limitations: selected repo audit only; external platform facts not reverified in preservation turn; many decisions are assistant recommendations.

## Ultra-Condensed Carry-Forward Capsule

This chat should be merged as a Dominium time-architecture source packet. It began with the user asking what happens to 32-bit OSes and applications after 2038. The core answer was that the failure mode is not bitness by itself, but signed 32-bit Unix-style time values in APIs, ABIs, storage formats, databases, and protocols. Systems with safe representations can continue; vulnerable time paths can fail. Clock rollback is not a general fix. Unsigned 32-bit absolute time is rejected because it only moves the cliff to 2106 and creates signedness/interoperability problems.

The user then constrained the desired time range to about 10,000 years forward and backward. The representation answer was that a single signed 64-bit scalar can span that range with 100 ns or 1 µs ticks, but not nanosecond ticks. Where one scalar is not required, a split representation (`int64 seconds + int32 nanoseconds`) is preferred for broad range and high fractional precision.

The user then asked for the most compatible future-proof software architecture. The durable framework is semantic separation: absolute instants, durations, monotonic elapsed-time counters, and civil/local time must be separate. This avoids Y2038, Y2K-style bugs, timezone/calendar rule drift, wall-clock jumps, and deterministic replay problems.

The key Dominium-specific portion came when the user asked to apply this to `julesc013/dominium` and requested docs/code reading. The assistant inspected selected repository files via GitHub. The strongest finding is that Dominium already largely has the right split: authoritative simulation time is logical ACT, not wall-clock; `dom_act_time_t` is signed 64-bit ACT seconds; DSYS owns platform/runtime monotonic microsecond timing; distributed/cross-shard ordering uses logical ticks and deterministic ordering keys; observer clocks are derived/non-authoritative; civil/astronomical conversions are placeholders/projections. Therefore the project likely does not need a time-model rewrite. It needs hardening.

Merge candidates for the master spec book: no authoritative wall-clock use; ACT is logical/monotonic/versioned; DSYS time is non-authoritative runtime timing; cross-shard messages carry logical ticks and deterministic ordering keys; observer/replay clocks are derived from ACT; civil/astronomical/lore time is a projection layer.

Open issues: audit all DSYS timer backends; freeze ACT unit/serialization semantics; verify save/replay/network formats do not use host `time_t`; add analyzer/CI checks for wall-clock leakage; design civil/astronomical projections; reverify external platform/library facts.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| P0 | Dominium ACT must remain logical authority, not wall-clock | Requirement candidate | DECISION-05 | Determinism/replay | FACT/INFERENCE | 5 |
| P0 | Audit DSYS backend timers | Task | TASK-01 | Platform edge risk | UNCERTAIN | 4 |
| P0 | Freeze ACT units and serialization | Task | TASK-03 | Compatibility | INFERENCE | 4 |
| P1 | Separate civil/astronomical time as projection | Requirement candidate | DECISION-08 | Prevents calendar leakage | INFERENCE | 4 |
| P1 | Verify external platform facts | Verification | VERIFY-01..04 | Avoid stale spec facts | UNCERTAIN | 4 |

## Workstream Summaries

* WORKSTREAM-01: 2038 and legacy time-risk analysis. Objective: avoid false assumptions about 32-bit systems. Next action: verify current platform docs.
* WORKSTREAM-02: Timestamp representation design. Objective: choose durable scalar/split representations. Next action: decide which representations apply to which Dominium boundary.
* WORKSTREAM-03: Cross-platform time framework. Objective: formalize Instant/Duration/Monotonic/Civil separation. Next action: convert into requirements.
* WORKSTREAM-04: Dominium time architecture mapping. Objective: harden ACT/DSYS/observer/projection layers. Next action: repo-wide time audit.
* WORKSTREAM-05: Preservation and aggregation. Objective: preserve this chat and merge later. Next action: save the generated package.

## Compact Registers for Merge

See `*_04_registers.md` for full compact registers. Highest-value IDs: DECISION-05, DECISION-06, DECISION-07, DECISION-08, TASK-01, TASK-03, CONSTRAINT-02, QUESTION-01, QUESTION-02, RISK-01, VERIFY-06, VERIFY-07.

## Possible Cross-Chat Duplicates

- Dominium deterministic ordering policy.
- Platform/runtime separation.
- Replay and save compatibility.
- Cross-shard message ordering.
- Civil/lore/astronomical time systems.

## Possible Cross-Chat Conflicts

- Any later proposal to drive authority from real-time/wall-clock.
- Any later migration that silently changes ACT units.
- Any design that treats observer clocks as authoritative.
- Any use of host ABI types in persistent schemas.

## Spec Book Integration Guidance

Feed this into chapters on time architecture, deterministic simulation, platform runtime, serialization/replay, and projection/civil time. Make no-wall-clock-authority a formal requirement. Keep external platform facts as background until verified. Do not merge ACT subsecond requirements prematurely; that remains an open design decision.

## Aggregator Warnings

Do not treat the repo inspection as exhaustive. Do not treat assistant recommendations as user-accepted decisions unless later confirmed. Do not erase the distinction between ACT, DSYS time, observer clocks, and civil projections.
