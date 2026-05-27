# Verification and Audit — Dominium UI Editor + Tool Editor Planning

## 1. Audit of the Original Context Transfer Packet

| Issue | Severity | Correction applied | Residual risk |
| --- | --- | --- | --- |
| Prompt artifacts were summarized rather than fully reproduced verbatim. | medium | This package adds stable artifact IDs, prompt purposes, command names, and file paths; exact prompt regeneration may still be needed. | Exact wording of long prompts is not fully embedded. |
| Uploaded files were listed but not inspected. | high | All uploaded files are marked UNCERTAIN / UNVERIFIED and added to verification queue. | Prior structural layout spec may not match screenshots exactly. |
| Implementation state was unknown. | high | Tasks and warnings explicitly state prompts are not implementation evidence. | Future assistant could still assume implementation if careless. |
| Some assistant recommendations were carried into plans. | medium | Decisions are labelled FACT vs INFERENCE; preview-host and domui_event statuses marked appropriately. | User may later reject some recommendations. |
| Tool Editor hardcoded substrate remained unresolved. | medium | Added QUESTION-09 and related risk. | Implementation prompt may need clarification. |
| IDE live editing interpretation may not match user intent. | medium-high | Added QUESTION-10, RISK-12, and verification item. | Requires user confirmation. |
| License policy partly assistant-generated. | medium | Marked GPL/LGPL policy as uncertain and added VERIFY-14. | Dependency choices still need review. |
| Setup tool path unknown. | high | Added QUESTION-05 and VERIFY-11. | UU5 path assumptions may fail. |

## 2. Final Reliability Assessment

- Completeness rating: 4/5
- Reliability rating: 4/5 for conversation-internal facts; 2/5 for actual repo implementation state.
- Aggregation readiness rating: 4/5
- Main remaining uncertainty sources: uninspected uploaded files, unknown repo state, unexecuted prompts, unconfirmed IDE interpretation, unknown setup target, and unconfirmed license policy.

## 3. Manual Verification Checklist

- VERIFY-01: Inspect repo/source bundle to verify existing DUI files and paths
- VERIFY-02: Confirm current CMake target names and build layout
- VERIFY-03: Confirm whether UI Editor implementation exists
- VERIFY-04: Confirm Tool Editor scope before implementation
- VERIFY-05: Verify TLV wire format and legacy import feasibility
- VERIFY-06: Verify backend capability details
- VERIFY-07: Run layout golden tests after implementation
- VERIFY-08: Confirm generated code commit policy
- VERIFY-09: Inspect LauncherC.zip screenshots if exact layout fidelity is needed
- VERIFY-10: Inspect SetupC.zip screenshots if exact setup layout fidelity is needed
- VERIFY-11: Confirm setup executable target and UI integration point
- VERIFY-12: Confirm preview-host approach for IDE live editing
- VERIFY-13: Verify AppKit/GTK backend availability or plan
- VERIFY-14: Clarify dependency license policy before adding third-party code
- VERIFY-15: Check all current external/tool version assumptions before use


## 4. Residual Risk Register
| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Assuming generated prompts were implemented | Future assistant may skip necessary work or trust nonexistent files. | medium | high | Verify repo state or ask user before acting. | WORKSTREAM-02 | FACT |
| RISK-02 | Treating screenshot bundle interpretation as verified | Layout specs may diverge from actual screenshots. | medium | medium | Inspect uploaded images before fidelity-sensitive work. | WORKSTREAM-13, WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| RISK-03 | Misreading Minecraft-style as graphical skinning | Would produce forbidden owner-draw/custom style work. | medium | high | Preserve “logical layout only, native controls only” constraint. | WORKSTREAM-13, WORKSTREAM-14 | FACT |
| RISK-04 | Overpromising pixel-perfect native parity across OS versions | Native controls vary by OS/theme/DPI. | medium | high | Use capability tiers and per-platform overrides; validate constraints. | WORKSTREAM-03, WORKSTREAM-05 | INFERENCE |
| RISK-05 | Windows bias leaking into canonical schema | Cross-platform Tool Editor/runtime could be compromised. | medium | high | Implement generic capability system early. | WORKSTREAM-05 | FACT |
| RISK-06 | Codegen overwrites user edits | Loss of developer work. | low-medium | high | Use gen/user split and append-only user stubs. | WORKSTREAM-08 | FACT |
| RISK-07 | Legacy import silently drops data | Existing launcher/setup UI behavior may be lost. | medium | high | Generate import reports with warnings and ID maps. | WORKSTREAM-10 | FACT |
| RISK-08 | Headless CLI opens GUI or depends on Win32 window init | Codex/CI automation fails. | medium | medium | Separate CLI paths from GUI initialization. | WORKSTREAM-11 | FACT |
| RISK-09 | Non-deterministic reports/artifacts | CI/goldens and git diffs become noisy. | medium | high | Sort outputs, avoid timestamps/absolute paths. | WORKSTREAM-15 | FACT |
| RISK-10 | Tool Editor self-hosting attempted too early | Schedule stalls on hard subsystem. | medium | medium-high | Validate UI Editor capability tests before Tool Editor. | WORKSTREAM-03 | INFERENCE |
| RISK-11 | Win95/Win9x compatibility mis-scoped | Could force unnecessary Phase A compromises or break future runtime goals. | medium | medium | Treat as capability/runtime tier unless user says editor host. | WORKSTREAM-05 | INFERENCE |
| RISK-12 | IDE live editing expectation mismatch | Preview-host approach may not satisfy user’s desire for IDE GUI tools. | medium | medium-high | Clarify before implementation. | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| RISK-13 | Dependency license policy misunderstood | Legal or redistribution risk. | low-medium | high | Verify before adding non-permissive deps. | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| RISK-14 | Mac/Linux native backends missing | Cross-platform preview/editor plans may be blocked. | high | medium | Verify backend availability; use null validation fallback if needed. | WORKSTREAM-16, WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| RISK-15 | Future aggregation treats assistant recommendations as user decisions | Spec book may include unaccepted requirements. | medium | high | Preserve labels and evidence. | WORKSTREAM-15 | FACT |
| RISK-16 | Over-compression of prompt artifacts | Future assistant may not recover implementation details. | medium | medium | Use artifact ledger and regenerate exact prompts if needed from summaries. | WORKSTREAM-15 | INFERENCE |

## 5. Recommended Re-Extraction Triggers
- Re-extract if the user provides actual Codex run results or repo diffs.
- Re-extract if uploaded screenshot bundles are inspected and differ materially from the structural spec.
- Re-extract if the user confirms or rejects IDE preview-host strategy.
- Re-extract after Tool Editor prompts are generated or implemented.
- Re-extract if a later chat changes canonical data format, platform scope, dependency policy, or native-widget requirement.
