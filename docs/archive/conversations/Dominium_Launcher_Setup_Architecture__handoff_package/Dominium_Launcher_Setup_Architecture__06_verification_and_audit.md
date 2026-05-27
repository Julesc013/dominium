# Verification and Audit — Dominium Launcher Setup Architecture

## 1. Audit of the Original Context Transfer Packet

| Issue | Severity | Correction applied | Residual risk |
|---|---|---|---|
| Original packet was strong but not normalized into stable IDs. | medium | This package adds WORKSTREAM/DECISION/TASK/CONSTRAINT/QUESTION/ARTIFACT/RISK/VERIFY IDs. | Low. |
| Original packet did not create downloadable files. | medium | This package exports Markdown/YAML files and ZIP archive. | Low after file creation. |
| Earlier C++98 launcher prompts could be confused with latest dsys/dgfx direction. | high | This package repeatedly marks C++98 frontend prompts as historical/superseded for launcher implementation. | Medium if future assistant ignores labels. |
| JSON vs TLV/dmeta contradiction remained unresolved. | high | This package elevates it to QUESTION-01, TASK-02, VERIFY-01, RISK-05. | Residual high until user/repo resolves it. |
| Repository state was not verified. | high | This package labels repo facts as unverified and adds verification queue items. | Residual high until repo inspection. |
| User profile preferences may come from project context rather than visible chat. | medium | This package labels those as PROJECT-CONTEXT. | Low. |
| Artifact tracking could have been more granular. | medium | This package adds ARTIFACT-01 through ARTIFACT-22. | Low. |
| Open questions and risks needed stable IDs. | medium | This package adds full registers. | Low. |

## 2. Final Reliability Assessment

- **Completeness rating:** 4/5
- **Reliability rating:** 4/5 for chat-state preservation; 2/5 for repository implementation facts because no repo was inspected.
- **Aggregation readiness rating:** 4/5
- **Main remaining uncertainty sources:**
  - Persistent format conflict.
  - Actual dsys/dgfx APIs.
  - Actual repo/build layout.
  - Setup language/platform-layer direction.
  - Runtime binary/capabilities implementation.

## 3. Manual Verification Checklist

- VERIFY-01: Final persistent format: JSON vs TLV `.dmeta`.
- VERIFY-02: Actual dsys and dgfx API names/signatures.
- VERIFY-03: Actual repository layout/build system.
- VERIFY-04: Setup implementation language and platform layer.
- VERIFY-05: Install path policy for retro platforms.
- VERIFY-06: Runtime binary names and capabilities support.
- VERIFY-07: Engine C ABI availability.
- VERIFY-08: dgfx support for text/fonts/icons/themes and 3D primitives.
- VERIFY-09: Network/browser/open URL support through dsys.
- VERIFY-10: File dialog/clipboard support through dsys.
- VERIFY-11: Dynamic plugin loading support.
- VERIFY-12: Whether project has existing TLV migrators.

## 4. Residual Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Future assistant follows superseded C++98/SDL/ncurses launcher plan. | Wrong implementation direction. | medium | high | Treat latest dsys/dgfx C89 launcher direction as active. | WORKSTREAM-05, WORKSTREAM-08 | FACT |
| RISK-02 | Codex invents dsys/dgfx API names. | Generated code may not compile. | high | high | Require repo inspection and adaptation to actual APIs. | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| RISK-03 | Tabs are implemented as decorative pages rather than full workflows. | Launcher fails user’s UX requirement. | medium | high | Carry detailed tab interaction model into work orders. | WORKSTREAM-06 | FACT |
| RISK-04 | Retro platform support overpromised. | Impossible or unusable implementation on CP/M/DOS/Win16. | medium | medium-high | Define explicit degradation paths and capability flags. | WORKSTREAM-08 | FACT |
| RISK-05 | JSON/TLV contradiction causes incompatible files. | Setup/launcher/tools disagree on manifests/config. | high | high | Resolve format decision before implementation. | WORKSTREAM-01, WORKSTREAM-04, WORKSTREAM-08 | FACT |
| RISK-06 | Engine determinism boundary leaks. | Simulation divergence or hidden coupling. | medium | high | Review includes/dependencies; keep launcher/setup out of engine. | WORKSTREAM-02 | FACT |
| RISK-07 | Runtime capabilities not implemented but launcher assumes them. | Instance launch selection fails. | medium | high | Implement or stub runtime capability probing clearly. | WORKSTREAM-03, WORKSTREAM-05 | FACT |
| RISK-08 | Plugin ABI changes silently. | Plugins break unpredictably. | medium | medium-high | Use ABI version checks and exported symbol contracts. | WORKSTREAM-07 | INFERENCE |
| RISK-09 | Setup uninstall deletes wrong data. | User data loss. | low-medium | critical | Preserve user data by default; conservative path checks. | WORKSTREAM-04 | FACT |
| RISK-10 | System install permissions mishandled. | Install/repair/uninstall fail or require unsafe elevation. | medium | medium | Separate portable/user/system logic and privilege boundaries. | WORKSTREAM-04 | FACT |
| RISK-11 | UI tree per-frame allocation too heavy for retro systems. | Memory/performance problems. | medium | medium | Use arenas/static pools and low-memory fallbacks. | WORKSTREAM-08 | INFERENCE |
| RISK-12 | Game becomes dependent on launcher paths/DB. | Standalone requirement violated. | medium | high | Runtime reads its own config/CLI; launcher metadata optional. | WORKSTREAM-03 | FACT |
| RISK-13 | Plugin failures crash launcher/setup. | Extensibility destabilizes core. | medium | medium-high | Core must run with zero plugins; plugin load failures logged/refused. | WORKSTREAM-07 | INFERENCE |
| RISK-14 | Package report treated as proof code exists. | Future implementation assumes nonexistent files. | medium | medium | Manifest/report states no repo was inspected and artifacts are proposed. | WORKSTREAM-01 | FACT |

## 5. Recommended Re-Extraction Triggers

- Re-extract if the original chat transcript is later found to contain omitted code/files not visible in this context.
- Re-extract after repo inspection if actual files contradict the proposed architecture.
- Re-extract if the user confirms JSON or TLV/dmeta, because many registers will become resolvable.
- Re-extract if the user revises the dsys/dgfx direction or reverts to earlier C++98 frontend implementation.
- Re-extract if other chat packages reveal conflicting decisions about setup/runtime/launcher boundaries.
