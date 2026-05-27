# Context Transfer Packet for a Future Chat — Dominium Timekeeping and 2038 Resilience

## 29.1 Ultra-Condensed Bootstrap Brief

This retired/archived chat focused on durable timekeeping for cross-platform software and its application to Dominium. The user first asked what happens to 32-bit operating systems and applications after 2038. The answer established that the main risk is not 32-bit hardware by itself, but signed 32-bit Unix-style time in APIs, ABIs, file formats, databases, protocols, and persisted data. Some systems keep working; vulnerable time-dependent functions can fail. Clock rollback is not a general fix. Signed 64-bit time is preferred over unsigned 32-bit absolute time.

The user then clarified that about 10,000 years into the future and past was enough. The representation discussion concluded that for one signed 64-bit scalar, 100 ns ticks or microsecond ticks are practical; nanosecond ticks are too narrow for that range. If not forced to one scalar, use `int64 seconds + int32 nanoseconds`.

The user then asked for the most compatible long-term software timekeeping framework. The answer was to separate semantic domains: absolute `Instant`, `Duration`, monotonic elapsed-time counters, and civil/local time. This avoids Y2038, Y2K-style bugs, wall-clock jumps, timezone changes, and deterministic replay failures.

The user then asked how this applies to Dominium and requested repo/docs/code reading from `Julesc013/dominium`. The assistant inspected selected GitHub repository files. Key repo-supported conclusions: Dominium’s authoritative simulation time is logical ACT, not wall-clock; `dom_act_time_t` is signed 64-bit ACT seconds; DSYS exposes monotonic microseconds for platform/runtime timing; deterministic ordering and cross-shard logs use logical ticks and stable keys; observer clocks are derived and non-authoritative; civil/astronomical conversions are currently placeholder projections. The important recommendation is not a rewrite, but boundary hardening: audit all DSYS backend timers, freeze ACT units and serialization, ensure platform event/build timestamps never affect authority, and keep civil/astronomical/lore time as derived projection.

The current task created a preservation package from an uploaded prompt. Treat assistant recommendations as recommendations unless user acceptance is explicit. Treat repo-backed findings as stronger but still limited to the files inspected.

## 29.2 Source Hierarchy

1. Direct user statements in this chat.
2. Explicit decisions accepted by the user.
3. Current task register.
4. Constraint register.
5. Artifact ledger.
6. Inferences from visible chat.
7. Assistant suggestions not accepted by the user.
8. General model knowledge.

## 29.3 Operating Rules for Future Assistants

- Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels.
- Do not re-ask answered questions unless missing information blocks correctness.
- Verify stale external facts before relying on them.
- Do not invent missing repo details.
- Do not treat tentative recommendations as accepted decisions.
- Do not repeat rejected options such as unsigned 32-bit absolute time or clock rollback.
- Keep ACT, DSYS runtime time, observer clocks, and civil time separate.
- Use structured outputs when continuing.

## 29.4 Active Workstreams

- WORKSTREAM-01: 2038 and legacy time-risk analysis.
- WORKSTREAM-02: Timestamp representation design.
- WORKSTREAM-03: Cross-platform durable time framework.
- WORKSTREAM-04: Dominium time architecture mapping and hardening.
- WORKSTREAM-05: Preservation and aggregation package.

## 29.5 Current Priorities

1. Audit DSYS backend timer implementations.
2. Freeze ACT unit/serialization semantics.
3. Add checks preventing wall-clock authority leakage.
4. Draft canonical Dominium time architecture documentation.
5. Verify current external platform facts before formal spec use.

## 29.6 Current Open Questions

- Do all DSYS backends provide safe monotonic 64-bit time on target platforms?
- Should Dominium ACT remain seconds permanently?
- What civil/astronomical/lore calendar model is needed?
- Which external platform facts have changed since the earlier answer?
- How should this report be merged with other Dominium preservation reports?

## 29.7 Recommended First Action

Start with a repo-wide audit plan for time usage: search for `time_t`, `time(`, `clock_gettime`, `GetTickCount`, `QueryPerformanceCounter`, `FILETIME`, `timestamp`, `act`, `tick`, `delivery_tick`, serialization of `dom_act_time_t`, and all DSYS backend `time_now_us` implementations. Classify each use as authoritative, runtime-only, diagnostic, serialization, or presentation.
