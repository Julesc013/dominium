# Reader Brief — Dominium UI Editor + Tool Editor Planning

## What This Chat Was About

This chat planned a Dominium/Domino UI authoring ecosystem. The immediate problem was a Windows launcher UI that looks mangled and flickers. The broader goal is a deterministic, native-widget UI authoring pipeline for launcher, setup, game, and other Dominium tools. The chat established that the repo already has an in-tree DUI system using TLV schema/state and backends including win32/comctl32, dgfx, and null. The selected strategy is Phase A UI Editor first, then Phase B Tool Editor. Phase A is Windows NT/latest / Windows 10+ only, system DPI, 100% design scale, and native Win32 preview. Phase B Tool Editor is the long-term cross-platform/self-hosting editor.

The chat produced a large set of Codex prompts, not verified implementation. These include an 11-prompt foundational plan, a final UI Editor implementation prompt, a six-prompt UU plan for import/CLI/ops/launcher/setup/hardening, and an IDE live-editing prompt. The user later clarified that Minecraft-style launcher/setup means logical layout only, not graphical design, and native Win32 widgets only.

## Most Important Things to Know

- UI Editor first, Tool Editor second.
- Existing DUI/TLV system is the foundation.
- TLV is canonical; JSON mirror is read-only/default if small.
- Do not assume any prompt was implemented.
- Native widgets are a hard requirement.
- Minecraft-style means structure only, not skinning.
- UI Editor must import existing tool UIs.
- UI Editor must expose CLI automation for Codex.
- ops.json is the deterministic edit DSL.
- Launcher/setup canonical docs are the capability tests.
- Tool Editor eventually self-hosts and edits itself/other tools.
- Uploaded files exist but were not inspected.
- IDE live editing prompt uses preview hosts; user acceptance of that approach is unverified.

## Active Plans or Workstreams

- Existing DUI system extension.
- Phase A UI Editor.
- Phase B Tool Editor.
- Canonical UI IR/TLV/JSON toolchain.
- Backend capability model.
- Deterministic layout engine.
- Splitter/Tabs/Scroll widgets.
- Action/event codegen.
- UI discovery/import/export.
- CLI and ops.json automation.
- Launcher/setup native logical layout tests.
- CI/determinism hardening.
- IDE live editing workflows.

## Decisions Already Made

- Phase A UI Editor precedes Tool Editor.
- Phase A is modern Windows-only, system DPI, 100% design scale.
- Tool Editor eventually targets all supported compiled systems.
- Use native OS controls.
- Use existing DUI; do not replace it with Qt/WPF/wx.
- TLV canonical with optional deterministic JSON mirror.
- Generic backend capability system.
- Splitter/Tabs/Scroll first-class in Phase A.
- Minecraft-style launcher/setup is logical layout only, native Win32 widgets only.

## Pending Tasks

- Verify whether any Codex prompts were executed.
- Inspect repo/source bundle.
- Implement or verify foundational prompts.
- Implement or verify UI Editor, CLI, ops.json engine.
- Generate launcher/setup canonical UI docs from scripts.
- Run hardening/determinism tests.
- Clarify IDE live-editing expectations.

## Open Questions

- Actual repo state and file paths.
- Actual TLV wire format.
- Setup tool location and UI integration.
- Generated code commit policy.
- Exact dependency license policy.
- Whether preview-host IDE strategy satisfies the user.
- Whether AppKit/GTK backends exist.

## Files / Artifacts / Prompts to Preserve

- `/mnt/data/source.zip`
- `/mnt/data/SetupC.zip`
- `/mnt/data/LauncherC.zip`
- `launcher_ui_v1.tlv`
- `dui_win32.c`, `dui_dgfx.c`, `dui_null.c`
- Prompts 1–11
- Final UI Editor prompt
- UU1–UU6 prompts
- IDE live editing prompt

## What to Verify Before Acting

- Whether prompts were implemented.
- Contents of uploaded zip files.
- Actual repo paths/targets.
- Existing TLV parser/writer.
- Setup tool existence.
- User acceptance of IDE preview-host approach.

## Best Next Step

If continuing implementation, first inspect the repo/source bundle or ask the user whether Codex executed any prompts. If continuing planning only, refine the IDE live-editing prompt or begin Tool Editor prompts after confirming UI Editor capability-test status.
