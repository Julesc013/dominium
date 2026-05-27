# Verification and Audit — Dominium Codex Platform Renderer API Plan

## 1. Audit of the Original Context Transfer Packet

| Issue | Severity | Correction applied | Residual risk |
| --- | --- | --- | --- |
| Uploaded repo unverified | high | Marked repo-specific claims as UNCERTAIN / UNVERIFIED and added verification queue. | Future assistant must still inspect archive/repo. |
| Earlier plans superseded | high | Added rejected/superseded register and active-plan markers. | Aggregator may still merge old plans unless careful. |
| AAA brainstorm could become accidental scope | medium | Marked as roadmap/background, not current implementation scope. | Future user may later promote items. |
| Exact prompt text not fully duplicated in all files | medium | Preserved active prompt IDs, names, purposes, outputs, and requirements. | Original chat may be needed for exact wording. |
| Tier-2 completeness caveat | medium | Added risk/open question about compile-gated vs runtime-complete. | May require later clarification. |
| User preferences could be overgeneralized | low | Separated explicit and inferred preferences. | Project-level preferences may differ in other chats. |
| Existing repo target names unknown | medium | Added open question and verification items. | Prompt execution must discover them. |

## 2. Final Reliability Assessment

- Completeness rating: 4/5
- Reliability rating: 4/5
- Aggregation readiness rating: 4/5
- Main remaining uncertainty sources:
  - Uploaded repo archive contents not inspected.
  - MASTER prompts 1-14 implementation status unknown.
  - Exact target names and current API surfaces unknown.
  - Some future AAA items are brainstorming, not decisions.
  - Tier-2 runtime completeness expectation may need clarification.

## 3. Manual Verification Checklist

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Inspect repo/archive to confirm MASTER prompts 1-14 implementation. | Prerequisite state unverified. | Repo search/build/history. | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Run initial CMake configure/build in repo. | Need actual build baseline. | cmake -S . -B build\verify_initial -G Ninja; build target help. | high | WORKSTREAM-02 | FACT |
| VERIFY-03 | Search DSYS/DGFX callsites. | API refactor depends on actual usage. | ripgrep dsys/domino_sys/dgfx. | high | WORKSTREAM-02, WORKSTREAM-03 | FACT |
| VERIFY-04 | Confirm exact launcher/game target names. | Prompt 8 command lines require exact names. | CMake target help. | high | WORKSTREAM-02 | FACT |
| VERIFY-05 | Run baseline header checker once implemented. | Validate C89/C++98 visibility. | CMake configure with checker. | high | WORKSTREAM-03 | FACT |
| VERIFY-06 | Print capability registry selection audit. | Ensure backend selection is deterministic/inspectable. | --print-selection output. | high | WORKSTREAM-03 | FACT |
| VERIFY-07 | Run domino_sys_smoke for win32 and win32_headless. | Tier-1 platform completion. | Prompt 4 commands. | high | WORKSTREAM-02 | FACT |
| VERIFY-08 | Run soft renderer hash test and dgfx_demo. | Tier-1 renderer completion. | Prompt 5 commands. | high | WORKSTREAM-02 | FACT |
| VERIFY-09 | Run Tier-2 incompatible-selection configure tests. | Gating correctness. | Prompt 6 bad platform/backend cmake calls. | medium-high | WORKSTREAM-02 | FACT |
| VERIFY-10 | Run TLV/handshake regression tests. | Serialization/network ABI correctness. | ctest or direct test exes. | high | WORKSTREAM-02 | FACT |
| VERIFY-11 | Run scripts\build_codex_verify.bat after Prompt 8. | Final done gate. | Verify script. | critical | WORKSTREAM-02 | FACT |
| VERIFY-12 | Confirm which AAA roadmap items become formal future requirements. | Brainstorm vs spec separation. | User review in future spec aggregation. | medium | WORKSTREAM-04 | INFERENCE |
| VERIFY-13 | Verify generated report files and ZIP are downloadable/readable. | Package quality. | Open files; check ZIP contents. | high | WORKSTREAM-05 | FACT |
| VERIFY-14 | Check whether existing CHANGELOG format exists. | Prompt 9 format compatibility. | Repo inspection. | low-medium | WORKSTREAM-02 | FACT |

## 4. Residual Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Repo-specific claims may be wrong because uploaded zip was not inspected. | Future assistant may implement against wrong file paths/API assumptions. | medium | high | Verify repo/archive before implementation-specific claims. | WORKSTREAM-01, WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| RISK-02 | MASTER prompts 1-14 may not actually be implemented. | Post-14 prompts may fail due missing prerequisites. | medium | high | Run verification searches/builds before execution. | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| RISK-03 | Final pack may not satisfy 'fully complete' for Tier-2 runtime backends. | User may expect runtime X11/Wayland/Cocoa/DX11/GL2/VK/Metal completion rather than compile-gated coverage. | medium | medium-high | Clarify if user reopens scope; add future runtime prompts. | WORKSTREAM-02 | INFERENCE |
| RISK-04 | Baseline header checker may flag many existing violations. | Prompt 1 could become larger than expected. | medium | high | Use stop-and-ask if rewriting/moving/deleting declarations needs policy. | WORKSTREAM-03 | INFERENCE |
| RISK-05 | Legacy DSYS vs new DSYS surface conflict. | Facade refactor may break callers. | medium | high | Keep legacy shim or ask policy per Prompt 1. | WORKSTREAM-03 | FACT |
| RISK-06 | Backend determinism grades may be hard to prove. | Incorrect D0 claims could break lockstep. | medium | high | Default uncertain optimized/platform-specific backends to D2 until proven. | WORKSTREAM-03 | INFERENCE |
| RISK-07 | AAA brainstorm could be mistaken as current scope. | Scope creep, implementation overload. | medium | medium | Label future features as roadmap/spec candidates only. | WORKSTREAM-04 | FACT |
| RISK-08 | Advanced presentation features could contaminate deterministic sim. | Replay/network desync. | low-medium | high | Keep presentation non-authoritative; use caps/extensions. | WORKSTREAM-04 | INFERENCE |
| RISK-09 | Report package may over-compress exact prompt text. | Future assistant may need original prompt wording. | low-medium | medium | Preserve active prompt IDs and key requirements; refer to chat context for exact text if needed. | WORKSTREAM-05 | INFERENCE |
| RISK-10 | Generated report may treat assistant suggestions as accepted decisions. | Spec book could overstate commitment. | low-medium | medium | Labels distinguish FACT/INFERENCE; future aggregator must preserve uncertainty. | WORKSTREAM-05 | FACT |
| RISK-11 | DX9 availability/toolchain mismatch. | Prompt 5 may fail to compile/link. | medium | medium | CMake detection and clear errors; system SDK only. | WORKSTREAM-02 | INFERENCE |
| RISK-12 | Smoke UI text requirement may exceed renderer IR subset. | Launcher/game smoke blocked. | medium | medium | Use rectangles or ask text strategy. | WORKSTREAM-02 | FACT |
| RISK-13 | TLV migration scope unknown. | Prompt 7 may miss legacy formats. | medium | high | Inventory formats before conversion. | WORKSTREAM-02 | FACT |
| RISK-14 | Verify script may be Windows-only. | Cross-platform CI needs later scripts. | low | medium | Accept for current Windows Codex; add POSIX scripts later if needed. | WORKSTREAM-02 | INFERENCE |
| RISK-15 | Stale external software/toolchain facts. | Build assumptions may age. | medium | medium | Reverify CMake/toolchain/SDK status before future use. | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| RISK-16 | Future aggregation may merge superseded plans incorrectly. | Project spec may include obsolete prompt packs. | medium | high | Use rejected/superseded register. | WORKSTREAM-05 | FACT |

## 5. Recommended Re-Extraction Triggers

- Re-extract this chat if a later chat changes the active prompt pack.
- Re-extract if the user confirms that master prompts 1-14 were or were not implemented.
- Re-extract if repository inspection contradicts this package.
- Re-extract if the user changes Tier-2 runtime-completion expectations.
- Re-extract if future chats promote AAA roadmap items into immediate implementation scope.
