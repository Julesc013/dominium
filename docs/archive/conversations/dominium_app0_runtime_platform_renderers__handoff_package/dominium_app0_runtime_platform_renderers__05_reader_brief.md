# Reader Brief — Dominium APP0 Runtime, Platform, and Renderer Architecture

## What This Chat Was About

This chat focused on Dominium / Domino APP0: the runtime/application/platform/renderer layer. The user provided an APP0 prompt defining client, server, launcher, setup/installer, tools, renderers, and platform support while forbidding simulation-rule redesign, content-definition changes, life/civ/economy changes, or gameplay shortcuts. The central boundary is that engine + game remain authoritative, while applications are shells and orchestrators.

A first assistant response produced a large Codex-style implementation pack, but the user then explicitly asked to discuss before planning or generating prompts. Discussion shifted to architectural correctness, missing enforcement mechanisms, and the eventual goal: a real executable capable of displaying an interactive, resizable window on supported platform/renderer combinations.

The chat then developed a proposed architecture: add or formalize a platform runtime layer for windows/events/surfaces/timing; keep renderers separate from window creation; bring up null and software rendering before GPU backends; treat GPU vendors as metadata rather than renderer families; use capability tiers and support classes for modern, legacy, vintage, and experimental targets; and consider runtime modules/plugins/manifests for plug-and-play distribution. The user granted write access to docs plus render, platform, application, client, and server, but not engine/game.

The most important unresolved item is repository verification. The user requested inspection of an old code snapshot in project attachments. A prior assistant claimed to inspect it, but that claim is unverified in this package. The next assistant should inspect the actual files before producing repo-specific plans or prompts.

## Most Important Things to Know

- APP0 scope is application/runtime/platform/render only.
- Engine + game remain authoritative.
- Applications are orchestrators, not decision-makers.
- Rendering never affects simulation.
- Client is non-authoritative.
- Server is authoritative and headless-capable.
- Launcher must not install content or alter simulation state.
- Setup owns install/version/integrity responsibilities.
- Tools must obey authority/law and be auditable.
- Current write permission covers docs plus render/platform/application/client/server only.
- Desired macro-plan end state includes a real interactive resizable window.
- Platform/windowing should be separate from rendering.
- Renderers should consume platform surfaces, not create windows.
- Null/software renderer path should come before GPU backends.
- Do not model renderers by GPU vendor.
- Module/plugin/framegraph/support-tier ideas are proposals, not accepted final decisions.
- Inspect old code snapshot before any repo-specific prompt or implementation plan.

## Active Plans or Workstreams

- WORKSTREAM-01 APP0 application/runtime layer.
- WORKSTREAM-02 Client runtime and window bring-up.
- WORKSTREAM-03 Server runtime.
- WORKSTREAM-04 Renderer architecture and capability model.
- WORKSTREAM-05 Platform runtime.
- WORKSTREAM-06 Launcher orchestration.
- WORKSTREAM-07 Setup/installer/integrity.
- WORKSTREAM-08 Tools and audit/authority.
- WORKSTREAM-09 Distribution/modules/plugins.
- WORKSTREAM-10 Old repo snapshot verification.

## Decisions Already Made

- APP0 is runtime/application layer only.
- Authoritative logic remains in engine + game.
- Client must not author authoritative state.
- Server must be authoritative and headless.
- Launcher must not install content or mutate sim state.
- Tools must obey same authority rules and be auditable.
- Do not generate more prompts until user asks after discussion/verification.
- Current permitted write areas exclude engine/game.

## Pending Tasks

- Inspect old repository snapshot.
- Verify actual directory layout.
- Verify build system/languages.
- Verify engine/game public APIs.
- Map dependency boundaries.
- Define platform runtime contract.
- Define renderer capability schema.
- Decide support classes and module strategy.
- Draft repo-specific architecture plan.
- Generate Codex prompts only when requested.

## Open Questions

- What is the actual repo tree?
- Is `app`, `apps`, or `application` canonical?
- Are engine/game APIs sufficient without modification?
- Do renderers already exist?
- Does platform runtime already exist?
- Static modules, dynamic plugins, or hybrid?
- Which platforms/renderers are canonical vs compatibility vs experimental?
- What is the setup trust model?
- What is the tools elevation/audit model?
- What are server sharding semantics?

## Files / Artifacts / Prompts to Preserve

- User APP0 prompt.
- Assistant APP0 implementation pack, with caveats.
- APP0 critique.
- Platform runtime proposal.
- Renderer/platform taxonomy proposal.
- Advanced runtime/module/framegraph proposal, with caveats.
- Prior Context Transfer Packet.
- This final report package.
- Old repo snapshot/project attachments, not yet verified.

## What to Verify Before Acting

- Actual old repository files.
- Build system and languages.
- Current client/server/render/platform dependencies.
- Engine/game public APIs.
- Whether renderers create windows.
- Whether server depends on graphics.
- Existing docs/tests.
- External graphics API/platform facts.

## Best Next Step

Inspect the old code snapshot/project attachments and produce a verified repository inventory with FACT / INFERENCE / UNCERTAIN labels before generating implementation prompts or architecture changes.
