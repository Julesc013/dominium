Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/Timekeeping_and_2038_Resilience/`
Promotion Status: not_reviewed

# Dominium Timekeeping and 2038 Resilience - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was mainly about making timekeeping code survive old platforms, future dates, deterministic simulation requirements, and project-scale architecture constraints. It began with a practical question: what happens to 32-bit operating systems and 32-bit applications after 2038? The user wanted to know whether they would stop working completely, whether critical functions would fail, whether rolling back the clock would work, and whether unsigned 32-bit or signed 64-bit integers could be used in 16-bit and 32-bit code to avoid the problem.

The conversation then moved from the general 2038 problem into representation design. The user clarified that they did not need millions of years of date support, only roughly 10,000 years into the future and past. This turned the problem into a range/precision tradeoff: with one signed 64-bit scalar, the chosen tick quantum determines the span. The assistant recommended either a single signed 64-bit scalar using 100 ns or microsecond ticks, or, preferably where possible, a split representation using `int64 seconds + int32 nanoseconds`.

The user then asked for the most compatible framework for cross-platform software intended to compile and run across past, present, and future target machines and operating systems. The answer shifted from arithmetic to architecture: durable code should not use one time type for everything. It should separate absolute instants, durations, monotonic elapsed-time measurement, and civil/local calendar time. This separation is the core future-proofing idea from the chat. It avoids not just Y2038, but also Y2K-style date-format bugs, wall-clock jumps, timezone rule changes, and replay nondeterminism.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, simulation, timekeeping, tooling, ui, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `15` source files. The primary extracted source is `docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__01_human_readable_report.md`.

## What Was Decided

- A future assistant should understand that this chat contributes a time architecture doctrine for Dominium: **ACT is authority; DSYS time is runtime-only; observer clocks are derived; civil/astronomical time is projection-only; wall-clock time must never drive authoritative ordering.
- What remains uncertain is the precise target list of legacy machines/toolchains and how far compatibility must go, especially for 16-bit compilers with weak or absent 64-bit arithmetic.
- The final topic is this export task. The user requested a human-readable report first, followed by registers, spec prep, context-transfer packet, aggregator packet, self-audit, and files. This package is designed to let the chat be read later without reopening the full transcript and to support merger into a larger Dominium spec book.
- The goal evolved from "will things break after 2038?" to "how should I design time for projects that should last?" and then to "does Dominium already match that doctrine?" The final upload changed the goal again into preservation and handoff.
- The exact acceptable precision for Dominium ACT is not established. The exact legacy OS/toolchain floor is not fully established inside this chat. The user has not explicitly accepted every assistant recommendation as final doctrine.
- Likely formal requirements include: authoritative logic must not depend on wall-clock time; ACT must remain versioned/fixed-width/logical; cross-shard ordering must use deterministic keys; platform time must remain DSYS-owned and non-authoritative; civil time must be projection-only.
- Which decisions were repo-grounded versus merely assistant suggestions?
- What external platform facts must be verified before formalizing the spec?
- The final user upload requested this preservation package. The purpose of this report is to preserve the chat for later reading and aggregation into a larger Dominium spec book.

## What Was Not Decided

- What remains uncertain is the current exact status of specific libc/OS/toolchain combinations, because those facts can change and were not reverified during this preservation turn.
- What remains uncertain is the precise target list of legacy machines/toolchains and how far compatibility must go, especially for 16-bit compilers with weak or absent 64-bit arithmetic.
- The main unresolved goals are backend audit, ACT serialization audit, civil/astronomical projection design, and verification of external platform facts.
- The main uncertainty is completeness of repo inspection. The assistant read key files, but not all serialization paths and not all platform backends.
- 6. Verify current platform/library facts before using them in formal public documentation.
- The preservation prompt explicitly requires a human-readable report first, not only a machine-readable handoff. It requires uncertainty labels, stable registers, preservation of artifacts, no invented facts, and downloadable files if tools are available. ?filecite?turn30file0?
- The user prefers source-grounded, audit-ready technical reasoning, direct structure, and careful distinction between facts, recommendations, and unresolved issues. PROJECT-CONTEXT indicates Dominium values C89/C++98 portability, deterministic architecture, CLI/TUI support, and clean platform/runtime separation.
- The strongest unresolved technical task is auditing actual backend timers and persistence formats.
- The main conclusion is that Dominium does not need a conceptual rewrite for time. It needs boundary hardening. Future work should audit all DSYS backends, freeze ACT units and serialization, ban wall-clock time from authority paths, make civil/astronomical time a derived projection layer, and verify any external platform facts before making them formal documentation.

## Ideas Rejected, Superseded, Or Deprioritised

- The chat rejected the idea that all 32-bit systems necessarily stop working after 2038. It rejected clock rollback as a general fix. It rejected unsigned 32-bit absolute time as a future-proof solution. It rejected one universal time type for all purposes. In the Dominium context, it rejected any design where wall-clock/platform timestamps drive authoritative ordering.
- Likely formal requirements include: authoritative logic must not depend on wall-clock time; ACT must remain versioned/fixed-width/logical; cross-shard ordering must use deterministic keys; platform time must remain DSYS-owned and non-authoritative; civil time must be projection-only.

## What Future Work Came From It

- The preservation task at the end changes the purpose of the chat from discussion to archive. The user uploaded a detailed preservation prompt requiring a human-readable report, structured registers, a context-transfer packet, a YAML-style spec sheet, an aggregator packet, audit sections, and downloadable files. This report is therefore both a reader-friendly reconstruction and a future-spec handoff.
- A future assistant should understand that this chat contributes a time architecture doctrine for Dominium: **ACT is authority; DSYS time is runtime-only; observer clocks are derived; civil/astronomical time is projection-only; wall-clock time must never drive authoritative ordering.
- The user then asked for the "most compatible" combination of timekeeping for cross-platform software architecture, including past and future target machines. The assistant answered with a layered model: absolute instant, duration, monotonic elapsed time, and civil/local time. This was the main conceptual upgrade of the chat. It broadened the issue from integer width to semantic separation.
- The user then uploaded a detailed prompt requiring this preservation package. The task became a maximum-fidelity archive and handoff for the current chat.
- The user should remember that unsigned 32-bit is not a future-proof absolute timestamp format. It only delays the overflow.
- The major future work is not to invent the model from scratch, but to harden boundaries and serialization.
- The final topic is this export task. The user requested a human-readable report first, followed by registers, spec prep, context-transfer packet, aggregator packet, self-audit, and files. This package is designed to let the chat be read later without reopening the full transcript and to support merger into a larger Dominium spec book.
- The user appears to be trying to prevent long-term architecture mistakes in Dominium and related C/C++ software. The user values deterministic simulation, legacy compatibility, future-proof serialization, and avoiding subtle date/time bugs that would require painful migrations later.
- The chat rejected the idea that all 32-bit systems necessarily stop working after 2038. It rejected clock rollback as a general fix. It rejected unsigned 32-bit absolute time as a future-proof solution. It rejected one universal time type for all purposes. In the Dominium context, it rejected any design where wall-clock/platform timestamps drive authoritative ordering.
- These rejections matter because future chats may otherwise repeat simplistic suggestions: "just use unsigned," "just set the clock back," or "just use one timestamp everywhere." Those ideas are inadequate for Dominium's deterministic simulation architecture.
- The preservation prompt explicitly requires a human-readable report first, not only a machine-readable handoff. It requires uncertainty labels, stable registers, preservation of artifacts, no invented facts, and downloadable files if tools are available. ?filecite?turn30file0?
- The main uploaded artifact is `Pasted text.txt`, the preservation prompt used to generate this package. ?filecite?turn30file0?

## Important Artifacts

- `handoff`: `1`
- `manifest`: `1`
- `markdown`: `3`
- `primary_report`: `1`
- `prompt`: `1`
- `reader_brief`: `2`
- `registers`: `1`
- `source_input`: `1`
- `spec_sheet`: `1`
- `verification`: `2`
- `zip`: `1`

## Verification Needed

- Verify every implementation, platform, tooling, release, and queue claim against current repo artifacts.
- Treat external platform or SDK claims as stale until independently checked.
- Treat old language-baseline claims as historical unless they match current `README.md` and current contracts.
- Do not infer current authority from the existence of this archive package.

## Candidate Promotions

Candidate promotions, if any, are recorded in `_promotion/PROMOTION_QUEUE.md`. This page does not promote claims.

## Do Not Assume

- Do not assume this conversation established current repo truth.
- Do not assume generated package reports are canonical.
- Do not assume old prompts were executed.
- Do not assume unresolved items are safe to implement.
- Do not use this package to open blocked work without stronger current authority.
