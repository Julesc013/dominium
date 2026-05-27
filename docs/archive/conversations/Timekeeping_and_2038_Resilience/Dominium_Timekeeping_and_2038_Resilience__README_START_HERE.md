# Start Here — Dominium Timekeeping and 2038 Resilience Complete Bundle

This bundle preserves and extends a conversation about Y2038, durable cross-platform timekeeping, and how those ideas apply to Dominium.

## Recommended reading order

1. `Dominium_Timekeeping_and_2038_Resilience__10_accompanying_detailed_summary_report.md` — newest companion narrative report; read this first for the whole story.
2. `Dominium_Timekeeping_and_2038_Resilience__01_human_readable_report.md` — formal preservation report from the earlier package.
3. `Dominium_Timekeeping_and_2038_Resilience__04_registers.md` — workstreams, decisions, tasks, risks, artifacts, verification queue.
4. `Dominium_Timekeeping_and_2038_Resilience__07_verification_and_audit.md` — caveats and verification items.
5. `Dominium_Timekeeping_and_2038_Resilience__02_context_transfer_packet.md` — use when continuing in a new chat.
6. `Dominium_Timekeeping_and_2038_Resilience__05_aggregator_packet.md` — use when merging with other chat reports.

## Core takeaway

Dominium's best timekeeping architecture is a separated model:

- ACT = authoritative logical simulation time.
- DSYS monotonic time = runtime-only platform pacing and measurement.
- Observer clocks = derived perception/replay layer.
- Civil/astronomical/lore time = projection layer, not authority.

## Main caveats

- The Dominium repo inspection was selective, not exhaustive.
- External platform facts should be reverified before formal publication.
- Some items are assistant recommendations, not explicit user-approved final decisions.

## Most important next action

Run a Dominium time audit focused on DSYS backend timers, ACT serialization, wall-clock leakage, and event timestamp usage.
