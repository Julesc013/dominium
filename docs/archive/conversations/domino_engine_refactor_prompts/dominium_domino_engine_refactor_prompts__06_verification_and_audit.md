# Verification and Audit — Dominium/Domino Engine Refactor Prompts

## 1. Audit of the Original Context Transfer Packet

| Issue | Severity | Correction applied | Residual risk |
|---|---|---|---|
| Previous packet lacked stable IDs for all registers. | medium | Added WORKSTREAM/DECISION/TASK/CONSTRAINT/etc. IDs throughout. | Exact prior prompt wording still summarized, not reproduced verbatim. |
| Repository state was unverified. | high | Marked repository/file/build claims as UNCERTAIN / UNVERIFIED and added verification queue. | Requires actual repo inspection. |
| Some assistant proposals could be mistaken for user decisions. | medium | Labeled accepted-by-continuation items as INFERENCE where appropriate. | Aggregator must preserve labels. |
| Exact Codex prompts are lengthy and not fully reproduced word-for-word. | medium | Captured prompt titles and detailed content summaries as artifacts. | If exact wording matters, review original transcript. |
| Plugin policy unresolved. | high | Added QUESTION-01/TASK-17/VERIFY-07. | Still requires user decision. |
| Exact fixed-point Q formats unresolved. | high | Added QUESTION-02/VERIFY-05. | Still requires numeric spec. |
| Rejected options were present but not normalized. | medium | Created REJECTED-01 through REJECTED-14. | Future chats may add more. |
| Documentation validation artifact needed clearer tracking. | low | Added WORKSTREAM-09 and ARTIFACT-29. | Requires actual docs pass. |

## 2. Final Reliability Assessment

- Completeness rating: 4/5.
- Reliability rating: 4/5 for visible-chat state; 2/5 for repository state because no repo was inspected.
- Aggregation readiness rating: 4/5 with caveats.
- Main remaining uncertainty sources: repository structure, exact prompt wording if needed verbatim, VM/native plugin policy, Q-format table, and whether later chats changed decisions.

## 3. Manual Verification Checklist

- VERIFY-01: Inspect actual repository structure and paths.
- VERIFY-02: Confirm build system and language standard enforcement.
- VERIFY-03: Confirm no files from prompts have already been created elsewhere.
- VERIFY-04: Confirm existing dsys/dgfx boundaries.
- VERIFY-05: Create or verify fixed-point Q-format table.
- VERIFY-06: Verify existing RES/TLV support and schema canonicalization.
- VERIFY-07: Decide deterministic VM versus native plugin policy.
- VERIFY-08: Verify current AGENT/JOB architecture if present.
- VERIFY-09: Check for existing ad-hoc graph implementations.
- VERIFY-10: Check for nondeterministic containers or raw memory hashing in existing code.
- VERIFY-11: Inspect existing BUILD/TRANS/STRUCT/DECOR or equivalents.
- VERIFY-12: Confirm existing space/DLC foundations.
- VERIFY-13: Confirm no engine code assumes grid-locked placement.
- VERIFY-14: Run documentation validation prompt after specs exist.
- VERIFY-15: Verify this package against original chat if exact prompt wording is needed.

## 4. Residual Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Repository assumptions may be wrong. | Codex prompts may reference wrong paths/build system. | medium | high | Inspect repository and adapt paths before applying. | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| RISK-02 | Semantic leakage into engine core. | Engine may hardcode game/DLC concepts, reducing extensibility. | medium | high | Use type IDs, TLV, generic primitives, review prompts/tests. | WORKSTREAM-04 | INFERENCE |
| RISK-03 | Over-modularization creates indirection/debug overhead. | Engine becomes harder to reason about or optimize. | medium | medium | Keep few core primitives and data-defined specializations. | WORKSTREAM-04 | INFERENCE |
| RISK-04 | Nondeterministic iteration or raw memory hashing. | Lockstep desyncs and replay mismatch. | high | high | Canonical sorted iteration and hash canonicalized data only. | WORKSTREAM-01 | FACT |
| RISK-05 | Budget deferral changes simulation outcomes instead of latency. | LOD/performance optimization changes game state. | medium | high | Use accumulators and invariant checks. | WORKSTREAM-04 | INFERENCE |
| RISK-06 | Agent behavior becomes unbounded or too expensive. | Large wildlife/worker simulations stall or desync. | medium | high | Instruction budgets, cadence decimation, group controllers, fields. | WORKSTREAM-03 | INFERENCE |
| RISK-07 | Fixed-point overflow/precision errors. | Incorrect physics, geometry, placement, or replay divergence. | medium | high | Define Q-format table and range tests. | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| RISK-08 | PRNG draw count divergence. | Same seed may produce different outcomes across agents/platforms. | medium | high | Use per-entity streams and structured draw policies. | WORKSTREAM-03 | INFERENCE |
| RISK-09 | Grid assumptions re-enter placement/building code. | Arbitrary placement requirement breaks. | medium | high | Regression scan for grid-locked logic; anchors as authority. | WORKSTREAM-07 | FACT |
| RISK-10 | Tolerance-based geometry/physics solvers creep in. | Cross-platform divergence. | medium | high | Fixed-iteration/exact construction only; docs/tests. | WORKSTREAM-02 | FACT |
| RISK-11 | Population/field models lose important individuals incorrectly. | Named/targeted agents vanish or desync. | medium | medium-high | Promotion/demotion invariants and stable IDs. | WORKSTREAM-03 | INFERENCE |
| RISK-12 | Compiled geometry/caches treated as source of truth. | Rebuild/replay inconsistency and loss of parametric editability. | medium | high | Source-of-truth vs derived-cache docs/tests. | WORKSTREAM-05 | FACT |
| RISK-13 | UI/renderer accesses truth instead of observer-filtered state. | Fog/knowledge cheating and replay mismatch. | medium | high | Observer-context query API and probe-only UI. | WORKSTREAM-06 | INFERENCE |
| RISK-14 | Equal-cost comms/visibility routes resolve nondeterministically. | Different machines see different information. | medium | high | Tie-break by stable IDs and canonical graph order. | WORKSTREAM-06 | INFERENCE |
| RISK-15 | DLC-specific concepts contaminate core. | Future content becomes harder to generalize. | medium | medium-high | Keep prompts semantic-free and content-defined. | WORKSTREAM-06 | FACT |
| RISK-16 | TRANS slot packing becomes content-specific rather than generic. | Road/rail/utility semantics hardcode into engine. | medium | medium | Use occupant category/type IDs and TLV parameters only. | WORKSTREAM-07 | INFERENCE |
| RISK-17 | Codex over-implements beyond prompt scope. | Gameplay semantics or unstable code introduced too early. | medium | medium-high | Each prompt says what not to implement; review diffs. | WORKSTREAM-08 | INFERENCE |
| RISK-18 | Documentation drift or contradictions. | Future implementers violate invariants. | medium | high | Run documentation validation prompt and keep validation report. | WORKSTREAM-09 | FACT |
| RISK-19 | This handoff overstates assistant proposals as accepted decisions. | Future assistant may treat tentative architecture as final user mandate. | low-medium | medium | Labels distinguish FACT from INFERENCE and unresolved questions. | WORKSTREAM-09 | INFERENCE |

## 5. Recommended Re-Extraction Triggers

- Re-extract if exact Codex prompt wording is required for legal/audit/version-control reasons.
- Re-extract if another chat superseded the 14-prompt plan.
- Re-extract if repository implementation diverges sharply from proposed paths.
- Re-extract if user clarifies native plugin policy or Q-format table in another chat.
- Re-extract if aggregation reveals conflicts with other old chat reports.
