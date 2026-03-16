Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Source: `docs/audit/auditx/FINDINGS.json`, `docs/audit/auditx/PROMOTION_CANDIDATES.json`
Generated UTC: 2026-02-15T06:52:05Z
Compatibility: AuditX Prompt 16 baseline
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# AUDITX Baseline Report

## Scan Summary
- Total findings: `1660`
- Severity counts: `INFO`=230, `RISK`=284, `VIOLATION`=145, `WARN`=1001
- Top analyzers by count: `A3_CANON_DRIFT`=605, `A6_UI_PARITY_BYPASS`=185, `A4_SCHEMA_USAGE`=160, `A7_LEGACY_CONTAMINATION`=160, `A5_CAPABILITY_MISUSE`=139, `A8_DERIVED_FRESHNESS_SMELL`=130, `A2_SCHEMA_SHADOWING`=120, `A1_REACHABILITY_ORPHANED`=80, `C2_MODE_FLAG_SMELL`=64, `A2_OWNERSHIP_BOUNDARY`=8, `A3_CAPABILITY_DRIFT`=5, `A4_DERIVED_ARTIFACT_CONTRACT`=1

## Highest-Confidence RISK Findings
- `C3_CAPABILITY_BYPASS_SMELL:0001` | `C3_CAPABILITY_BYPASS_SMELL` | confidence `0.82` | `client/core/client_command_bridge.c` | Bridge is missing required capability/entitlement guard markers.
- `A6_UI_PARITY_BYPASS:0003` | `A6_UI_PARITY_BYPASS` | confidence `0.80` | `client/ui/workspaces/session_transition/session_transition.default.json` | Command appears only in UI-facing files.
- `A6_UI_PARITY_BYPASS:0004` | `A6_UI_PARITY_BYPASS` | confidence `0.80` | `client/ui/workspaces/session_transition/session_transition.default.json` | Command appears only in UI-facing files.
- `A6_UI_PARITY_BYPASS:0005` | `A6_UI_PARITY_BYPASS` | confidence `0.80` | `client/ui/workspaces/session_transition/session_transition.default.json` | Command appears only in UI-facing files.
- `A6_UI_PARITY_BYPASS:0006` | `A6_UI_PARITY_BYPASS` | confidence `0.80` | `client/ui/workspaces/session_transition/session_transition.default.json` | Command appears only in UI-facing files.
- `A6_UI_PARITY_BYPASS:0007` | `A6_UI_PARITY_BYPASS` | confidence `0.80` | `client/ui/workspaces/session_transition/session_transition.default.json` | Command appears only in UI-facing files.
- `A6_UI_PARITY_BYPASS:0011` | `A6_UI_PARITY_BYPASS` | confidence `0.80` | `packs/tool/pack.tool.inspector/ui/window.inspector.json` | Command appears only in UI-facing files.
- `A6_UI_PARITY_BYPASS:0014` | `A6_UI_PARITY_BYPASS` | confidence `0.80` | `packs/tool/pack.tool.log_viewer/ui/window.log.json` | Command appears only in UI-facing files.
- `A6_UI_PARITY_BYPASS:0015` | `A6_UI_PARITY_BYPASS` | confidence `0.80` | `packs/tool/pack.tool.log_viewer/ui/window.log.json` | Command appears only in UI-facing files.
- `A6_UI_PARITY_BYPASS:0017` | `A6_UI_PARITY_BYPASS` | confidence `0.80` | `packs/tool/pack.tool.navigation/ui/window.goto.json` | Command appears only in UI-facing files.
- `A6_UI_PARITY_BYPASS:0019` | `A6_UI_PARITY_BYPASS` | confidence `0.80` | `packs/tool/pack.tool.navigation/ui/window.navigator.json` | Command appears only in UI-facing files.
- `A6_UI_PARITY_BYPASS:0021` | `A6_UI_PARITY_BYPASS` | confidence `0.80` | `packs/tool/pack.tool.navigation/ui/window.site_browser.json` | Command appears only in UI-facing files.
- `A6_UI_PARITY_BYPASS:0023` | `A6_UI_PARITY_BYPASS` | confidence `0.80` | `packs/tool/pack.tool.time_control/ui/window.time.json` | Command appears only in UI-facing files.
- `A6_UI_PARITY_BYPASS:0038` | `A6_UI_PARITY_BYPASS` | confidence `0.80` | `tools/launcher/ui/doc/launcher_ui_doc.json` | Command appears only in UI-facing files.
- `A6_UI_PARITY_BYPASS:0039` | `A6_UI_PARITY_BYPASS` | confidence `0.80` | `tools/launcher/ui/doc/launcher_ui_doc.json` | Command appears only in UI-facing files.
- `A6_UI_PARITY_BYPASS:0040` | `A6_UI_PARITY_BYPASS` | confidence `0.80` | `tools/launcher/ui/doc/launcher_ui_doc.json` | Command appears only in UI-facing files.
- `A6_UI_PARITY_BYPASS:0041` | `A6_UI_PARITY_BYPASS` | confidence `0.80` | `tools/launcher/ui/doc/launcher_ui_doc.json` | Command appears only in UI-facing files.
- `A6_UI_PARITY_BYPASS:0042` | `A6_UI_PARITY_BYPASS` | confidence `0.80` | `tools/launcher/ui/doc/launcher_ui_doc.json` | Command appears only in UI-facing files.
- `A6_UI_PARITY_BYPASS:0043` | `A6_UI_PARITY_BYPASS` | confidence `0.80` | `tools/launcher/ui/doc/launcher_ui_doc.json` | Command appears only in UI-facing files.
- `A6_UI_PARITY_BYPASS:0044` | `A6_UI_PARITY_BYPASS` | confidence `0.80` | `tools/launcher/ui/doc/launcher_ui_doc.json` | Command appears only in UI-facing files.

## Promotion Candidates (RepoX/TestX)
- `INVARIANT_HARDEN` | ruleset `core.json` | risk_score `0.980` | evidence `docs/audit/auditx/FINDINGS.json` | Promote repeated high-confidence semantic risk into static governance.
- `INVARIANT_HARDEN` | ruleset `core.json` | risk_score `0.900` | evidence `.xstack_cache/ws-1fc8358ec83405db/auditx/entries/6585b5a54ee7182cf00be45d3ff185a3c3fe56009c35917cdd3932154dedc9f4.json, .xstack_cache/ws-7bb944ef38ea1547/artifacts/repox_runner/proof_manifest.json, .xstack_cache/ws-7bb944ef38ea1547/repox_runner/9535adbdc0f7acaecbf052e8b1c04413ef2f816a4c76327dcd996d47aef5ec5a.json, .xstack_cache/ws-9c43ae0f17388d09/auditx/entries/33a11328dff9a2912ab1ef68d06b7cf662c05f8114cf55b73191d86ea483aabb.json, .xstack_cache/ws-9c43ae0f17388d09/auditx/entries/834f187e42fa7ce6498378fae8289a6b8bf8e750d4f762f0f0edd085f2527981.json, .xstack_cache/ws-9c43ae0f17388d09/auditx/entries/9adddc3063a3a1a6d947c4227cbbbce819cf7e95d7c10d18752e3fe282f5807f.json, .xstack_cache/ws-9c43ae0f17388d09/auditx/entries/9b0b04b32c90968f48a0242abd89b106b7eeac525c777a83c8ec31d772cbb40a.json, .xstack_cache/ws-9c43ae0f17388d09/auditx/entries/b27603ffd2278b00f95e87cdec5ff24001293fd019dfd57b37656bbb8673fbc8.json, .xstack_cache/ws-9c43ae0f17388d09/auditx/entries/ecb859c1c62e8738783dac5c514bf64a8c50a4b1cf6ff48f071bd14fee648c10.json, .xstack_cache/ws-9c43ae0f17388d09/auditx/entries/f09c8589ec4c915fa763d56a88504412fb313266926eb52036018e65aeab3900.json (+54 more)` | Promote repeated high-confidence semantic risk into static governance.
- `INVARIANT_HARDEN` | ruleset `core.json` | risk_score `0.900` | evidence `legacy/README.md, legacy/_orphaned/engine_has_launcher_module/launcher/CMakeLists.txt, legacy/_orphaned/legacy_source_common/common/CMakeLists.txt, legacy/_orphaned/legacy_source_game/game/CMakeLists.runtime.txt, legacy/_orphaned/legacy_source_game/game/CMakeLists.txt, legacy/_orphaned/legacy_source_game/game/README.md, legacy/_orphaned/legacy_source_game/game/SPEC_COMMANDS.md, legacy/_orphaned/legacy_source_game/game/SPEC_CONTENT.md, legacy/_orphaned/legacy_source_game/game/SPEC_REPLAY.md, legacy/_orphaned/legacy_source_game/game/SPEC_RUNTIME.md (+71 more)` | Promote repeated high-confidence semantic risk into static governance.
- `TEST_REGRESSION` | ruleset `core.json` | risk_score `0.615` | evidence `client/core/client_command_bridge.c` | Promote repeated high-confidence semantic risk into static governance.
- `INVARIANT_HARDEN` | ruleset `core.json` | risk_score `0.600` | evidence `data/registries/glossary.json, docs/architecture/TERMINOLOGY_GLOSSARY.md` | Promote repeated high-confidence semantic risk into static governance.
- `TEST_REGRESSION` | ruleset `core.json` | risk_score `0.600` | evidence `client/ui/workspaces/session_transition/session_transition.default.json, packs/tool/pack.tool.inspector/ui/window.inspector.json, packs/tool/pack.tool.log_viewer/ui/window.log.json, packs/tool/pack.tool.navigation/ui/window.goto.json, packs/tool/pack.tool.navigation/ui/window.navigator.json, packs/tool/pack.tool.navigation/ui/window.site_browser.json, packs/tool/pack.tool.time_control/ui/window.time.json, tools/launcher/ui/doc/launcher_ui_doc.json, tools/launcher/ui/gen/ui_launcher_ui_actions_gen.cpp, tools/launcher/ui/registry/launcher_actions_registry.json (+6 more)` | Promote repeated high-confidence semantic risk into static governance.
- `INVARIANT_HARDEN` | ruleset `core.json` | risk_score `0.585` | evidence `client/app/main_client.c, client/shell/client_shell.c` | Promote repeated high-confidence semantic risk into static governance.
- `INVARIANT_HARDEN` | ruleset `derived.json` | risk_score `0.570` | evidence `.xstack_cache/auditx/RUN_META.json, .xstack_cache/performx/RUN_META.json, .xstack_cache/repox/REPOX_PROFILE.json, .xstack_cache/repox/proof_manifest.json, .xstack_cache/securex/RUN_META.json, .xstack_cache/testx/TESTX_RUN_META.json, .xstack_cache/xstack/FULL_PLAN_TOO_LARGE.md, docs/audit/perf/profile_trace.sample.json, docs/audit/system/LEDGER_SNAPSHOT.md, docs/audit/xstack/PERFORMANCE_CEILING_ALERT.md` | Promote repeated high-confidence semantic risk into static governance.
- `INVARIANT_HARDEN` | ruleset `core.json` | risk_score `0.555` | evidence `client/gui/client_app_win32.cpp, client/ui/workspaces/session_transition/session_transition.default.json, launcher/gui/launcher_app_win32.cpp, launcher/gui/win32/launcher_app_win32.cpp, packs/tool/pack.tool.inspector/ui/window.inspector.json, packs/tool/pack.tool.log_viewer/ui/window.log.json, packs/tool/pack.tool.navigation/ui/window.goto.json, packs/tool/pack.tool.navigation/ui/window.navigator.json, packs/tool/pack.tool.navigation/ui/window.site_browser.json, packs/tool/pack.tool.time_control/ui/window.time.json (+14 more)` | Promote repeated high-confidence semantic risk into static governance.
- `TEST_REGRESSION` | ruleset `core.json` | risk_score `0.525` | evidence `setup/packages/scripts/packaging/pipeline.py, tools/auditx/analyzers/a1_reachability_orphaned.py, tools/auditx/analyzers/a5_capability_misuse.py, tools/auditx/analyzers/a6_ui_parity_bypass.py, tools/auditx/analyzers/a7_legacy_contamination.py, tools/auditx/analyzers/c2_mode_flag_smell.py, tools/auditx/cache/vs2026/entries/00039f76f9f9aa7612e2ac3f5a5661ef0afdfb00d60ee7df3bfe4765b0e4eefe.json, tools/auditx/cache/vs2026/entries/004e9e6091e72c9f2540085dee6741e349b0f8c354975941901b2e5a3aa7db70.json, tools/auditx/cache/vs2026/entries/00eb8f6b63c89cffb2d004e3443eac5b795622614c250fdcd357b9caa9a3aff7.json, tools/auditx/cache/vs2026/entries/01ad6e641ca1fa9bb6d37309dd9aeb6e67a692d893139456b7201f867fe3db16.json (+70 more)` | Promote repeated high-confidence semantic risk into static governance.

## Open Debt Map
- By recommended action: `ADD_RULE`=543, `ADD_TEST`=431, `DOC_FIX`=606, `RETIRE`=80
- By status: `OPEN`=1660
- Dominant analyzer domains: `A3_CANON_DRIFT`=605, `A6_UI_PARITY_BYPASS`=185, `A4_SCHEMA_USAGE`=160, `A7_LEGACY_CONTAMINATION`=160, `A5_CAPABILITY_MISUSE`=139, `A8_DERIVED_FRESHNESS_SMELL`=130, `A2_SCHEMA_SHADOWING`=120, `A1_REACHABILITY_ORPHANED`=80

## Promotion Guidance
- Promote repeated high-confidence structural findings to RepoX invariants when they are machine-checkable without semantic ambiguity.
- Promote repeated behavior regressions to TestX when they can be reproduced deterministically from fixtures.
- Keep informational findings in AuditX until false-positive rate is reduced and ownership is clear.

## TODO
- Curate and prune low-confidence findings to reduce triage noise.
- Promote at least two stable candidates into RepoX/TestX in the next governance pass.
- Add longitudinal trend deltas between baseline snapshots.
