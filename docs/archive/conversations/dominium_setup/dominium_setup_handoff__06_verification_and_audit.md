# Verification and Audit — Dominium Setup Handoff

## 1. Audit of the Original Context Transfer Packet

| Issue | Severity | Correction applied | Residual risk |
| --- | --- | --- | --- |
| Applied Codex prompts were summarized, not fully reproduced. | medium | This package captures their titles, phases, mandatory effects, and verification needs. | Exact wording may still need original transcript if replaying prompts verbatim. |
| Actual repo state was unverified. | high | Marked all repo-state claims as UNCERTAIN / UNVERIFIED and added verification queue. | None until repo is inspected. |
| Assistant proposals could be confused with decisions. | high | Added labels and rejected/superseded registers; marked libs/appcmd/UI IR path as tentative. | Aggregator must preserve labels. |
| Old directory structures could be reused accidentally. | high | Added explicit rejected/superseded options and canonical layout. | Future assistant may ignore report; emphasize next actions. |
| Artifact tracking was broad but not ID-normalized. | medium | Normalized artifacts ARTIFACT-01..23. | Some large prompt bodies remain summarized. |
| Task order needed sharper first action. | medium | Added recommended task order and verification checklist. | Implementation still depends on repo access. |
| Project-level context from other chats could be mistaken as native to this chat. | medium | Marked as PROJECT-CONTEXT where applicable. | Pasted context is visible but provenance remains external. |
| External/toolchain facts might become stale. | medium | Added staleness warnings and verification queue. | Future users must verify current tooling. |

## 2. Final Reliability Assessment

| Metric | Rating | Notes |
|---|---:|---|
| Completeness | 4 / 5 | Covers visible chat, previous packet, main prompts, decisions, tasks, risks, artifacts. Exact full text of all large prompts is not reproduced. |
| Reliability | 4 / 5 | Strong for chat-specific decisions; repo implementation state unverified. |
| Aggregation readiness | 4 / 5 | Stable IDs and labels provided; needs cross-chat deduplication. |
| Staleness risk | medium | Build/tool/repo facts must be verified before use. |

Main remaining uncertainty sources:
- actual repository state,
- whether hardening prompt was executed,
- actual schema and contract files,
- current CMake/CTest status,
- exact RepoX/TestX implementation.

## 3. Manual Verification Checklist

| ID | Check | Purpose |
| --- | --- | --- |
| VERIFY-01 | Current setup/ tree | Needed to determine actual post-refactor state. |
| VERIFY-02 | Current schema/ tree | Schema-backed setup I/O is required. |
| VERIFY-03 | libs/contracts existence and CMake target | Neutral contracts are mandatory. |
| VERIFY-04 | CMake configure/build/test | Build claims require proof. |
| VERIFY-05 | setup --help and launcher --help | Smoke tests required by prompts. |
| VERIFY-06 | verify_tree_sanity and verify_includes_sanity scripts | Boundary enforcement must work. |
| VERIFY-07 | docs/SETUP_GAPS.md and related setup docs | Shows generated hardening prompt executed. |
| VERIFY-08 | setup/core/fetch offline/network behavior | Capability accepted but implementation unknown. |
| VERIFY-09 | update/downgrade operation semantics | Required flows need explicit schemas/tests. |
| VERIFY-10 | UI IR and binding validation path | Canon requires UI as data. |
| VERIFY-11 | RepoX/TestX/BUILD-ID tooling status | Release governance depends on it. |
| VERIFY-12 | Legacy platform support status | Avoids assuming implementation exists. |
| VERIFY-13 | Old IDE artifacts are quarantined or non-authoritative | Prevents IDE build drift. |
| VERIFY-14 | Docs status-header policy | CLEAN-2/canon management requires it. |
| VERIFY-15 | This package contents after generation | Ensure files and ZIP saved correctly. |

## 4. Residual Risk Register

| ID | Risk | Consequence | Mitigation | Label |
| --- | --- | --- | --- | --- |
| RISK-01 | Future assistant follows obsolete adapters/packaging/source layout. | Canonical setup structure may be corrupted. | Always start from latest canonical setup/ layout. | FACT / INFERENCE |
| RISK-02 | Assistant suggestions are mistaken for user decisions. | Spec may harden tentative ideas incorrectly. | Keep FACT/INFERENCE labels and require user/canon confirmation. | FACT |
| RISK-03 | Repo state differs from this packet. | Implementation may target missing or moved files. | Inspect repo before acting. | UNCERTAIN / UNVERIFIED |
| RISK-04 | Launcher duplicates setup update/repair logic. | Authority and audit guarantees break. | Use setup invocation + schema reports only. | FACT |
| RISK-05 | Engine purity regresses. | Engine becomes unreusable and contaminated. | Run tree/include sanity checks in CI. | FACT |
| RISK-06 | Ad-hoc setup formats drift from schema. | Launcher/setup incompatibility and unverifiable state. | Execute schema normalization phase. | FACT / INFERENCE |
| RISK-07 | GUI/TUI embeds business logic. | CLI parity and determinism are broken. | Use command graph + UI IR binding validation. | FACT / PROJECT-CONTEXT |
| RISK-08 | Network install becomes required unintentionally. | Offline/air-gapped support fails. | Test offline install paths and treat network as transport. | FACT / INFERENCE |
| RISK-09 | Rollback is under-tested. | Partial installs may corrupt state. | Fault-injection tests for each transaction phase. | FACT |
| RISK-10 | Build metadata/changelog manually edited. | Release traceability lost. | Use RepoX-generated outputs only. | FACT / PROJECT-CONTEXT |
| RISK-11 | Legacy platform goals impose modern app constraints on engine/game. | Toolchain compatibility breaks. | Keep app toolchains isolated from engine/game. | FACT |
| RISK-12 | Context package omits exact old prompt wording. | Future re-execution may miss nuance. | Use artifact ledger and request original prompt if exact replay required. | UNCERTAIN / UNVERIFIED |
| RISK-13 | Future aggregation deduplicates conflicting chats too aggressively. | Contradictions may be erased. | Preserve provenance and contradictions during aggregation. | FACT |
| RISK-14 | Dates/tool versions become stale. | Build instructions may fail later. | Verify external/toolchain facts before use. | FACT |
| RISK-15 | Generated report files are edited manually and diverge. | Aggregation data integrity weakens. | Store ZIP and Markdown/YAML together; note manual changes. | FACT |

## 5. Recommended Re-Extraction Triggers

- Re-extract if the actual repo after Codex prompts differs substantially from this packet.
- Re-extract if the setup hardening prompt has already been executed and produced new docs/tasks.
- Re-extract if CANON_INDEX.md contradicts any application-layer or setup assumption here.
- Re-extract if UI IR/app command spine paths are canonically settled elsewhere.
- Re-extract if future aggregation discovers conflicting chat reports.
